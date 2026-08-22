"""Database test suite for StockPilot (TC-DB-01..14).

Safe to run against the dev database: every write happens inside a transaction
that is ALWAYS rolled back, so nothing is persisted. Read-only checks touch
nothing. Produces PASS/FAIL evidence for the database test plan.
"""
import asyncio, uuid, logging
logging.disable(logging.CRITICAL)
from sqlalchemy import text
from app.db.session import engine

PASS, FAIL = "PASS", "FAIL"
results = []

U_COLS = "(id,email,password_hash,full_name,role,is_active)"


def rec(tid, desc, ok):
    results.append((tid, desc, PASS if ok else FAIL))


async def violates(conn, sql, params=None):
    """Return True if the statement is correctly REJECTED by a constraint."""
    sp = await conn.begin_nested()
    try:
        await conn.execute(text(sql), params or {})
        await sp.rollback()
        return False
    except Exception:
        await sp.rollback()
        return True


async def new_user(conn, email=None):
    uid = str(uuid.uuid4())
    await conn.execute(text(f"INSERT INTO users {U_COLS} VALUES (:i,:e,'x','x','investor',true)"),
                       {"i": uid, "e": email or f"{uuid.uuid4()}@t.io"})
    return uid


async def main():
    async with engine.connect() as conn:
        outer = await conn.begin()
        uid = (await conn.execute(text("SELECT id FROM users LIMIT 1"))).scalar()

        # TC-DB-01
        tbls = (await conn.execute(text(
            "SELECT count(*) FROM information_schema.tables WHERE table_schema='public'"))).scalar()
        rec("TC-DB-01", f"Schema: {tbls} tables present in public schema", tbls >= 12)

        # TC-DB-02  UNIQUE email
        ok = await violates(conn,
            f"INSERT INTO users {U_COLS} VALUES (:i,(SELECT email FROM users LIMIT 1),'x','x','investor',true)",
            {"i": str(uuid.uuid4())})
        rec("TC-DB-02", "UNIQUE(email): duplicate email rejected", ok)

        # TC-DB-03  NOT NULL email
        ok = await violates(conn,
            f"INSERT INTO users {U_COLS} VALUES (:i,NULL,'x','x','investor',true)", {"i": str(uuid.uuid4())})
        rec("TC-DB-03", "NOT NULL(email): null email rejected", ok)

        # TC-DB-04  enum role
        ok = await violates(conn,
            f"INSERT INTO users {U_COLS} VALUES (:i,:e,'x','x','superuser',true)",
            {"i": str(uuid.uuid4()), "e": f"{uuid.uuid4()}@t.io"})
        rec("TC-DB-04", "ENUM(role): invalid role value rejected", ok)

        # TC-DB-05  FK integrity
        ok = await violates(conn,
            "INSERT INTO holdings (id,user_id,ticker,quantity,avg_cost) VALUES (:i,:u,'AAPL',1,1)",
            {"i": str(uuid.uuid4()), "u": str(uuid.uuid4())})
        rec("TC-DB-05", "FOREIGN KEY: holding with unknown user_id rejected", ok)

        # TC-DB-06  cascade delete
        sp = await conn.begin_nested()
        tu = await new_user(conn); th = str(uuid.uuid4())
        await conn.execute(text("INSERT INTO holdings (id,user_id,ticker,quantity,avg_cost) "
            "VALUES (:i,:u,'AAPL',1,1)"), {"i": th, "u": tu})
        await conn.execute(text("DELETE FROM users WHERE id=:u"), {"u": tu})
        left = (await conn.execute(text("SELECT count(*) FROM holdings WHERE id=:h"), {"h": th})).scalar()
        await sp.rollback()
        rec("TC-DB-06", "ON DELETE CASCADE: child holding removed with user", left == 0)

        # TC-DB-07  watchlist UNIQUE(user_id,ticker)
        sp = await conn.begin_nested()
        await conn.execute(text("INSERT INTO watchlist (id,user_id,ticker) VALUES (:i,:u,'ZTEST')"),
                           {"i": str(uuid.uuid4()), "u": str(uid)})
        ok = await violates(conn, "INSERT INTO watchlist (id,user_id,ticker) VALUES (:i,:u,'ZTEST')",
                            {"i": str(uuid.uuid4()), "u": str(uid)})
        await sp.rollback()
        rec("TC-DB-07", "UNIQUE(user_id,ticker): duplicate watchlist entry rejected", ok)

        # TC-DB-08  server-side default
        sp = await conn.begin_nested()
        du = await new_user(conn)
        row = (await conn.execute(text("SELECT created_at,updated_at FROM users WHERE id=:i"),
                                  {"i": du})).first()
        await sp.rollback()
        rec("TC-DB-08", "DEFAULT: created_at / updated_at auto-populated by the database",
            row[0] is not None and row[1] is not None)

        # TC-DB-09  JSONB weights round-trip
        sp = await conn.begin_nested()
        sid = str(uuid.uuid4())
        await conn.execute(text("INSERT INTO strategies (id,owner_id,name,weights,is_preset,is_published) "
            "VALUES (:i,:u,'t',CAST(:w AS jsonb),false,false)"),
            {"i": sid, "u": str(uid), "w": '{"sentiment":20,"momentum":30}'})
        w = (await conn.execute(text("SELECT weights->>'momentum' FROM strategies WHERE id=:i"),
                                {"i": sid})).scalar()
        await sp.rollback()
        rec("TC-DB-09", f"JSONB(weights): stored & queried nested value momentum={w}", w == "30")

        # TC-DB-10  role subtype 1:1
        row = (await conn.execute(text(
            "SELECT (SELECT count(*) FROM users), "
            "(SELECT count(*) FROM investors)+(SELECT count(*) FROM analysts)+(SELECT count(*) FROM admins)"))).first()
        rec("TC-DB-10", f"Role subtype tables: {row[0]} users = {row[1]} profile rows (1:1 mapping)", row[0] == row[1])

        # TC-DB-11  singleton
        cnt = (await conn.execute(text("SELECT count(*) FROM platform_settings"))).scalar()
        rec("TC-DB-11", f"Singleton: platform_settings holds exactly {cnt} row", cnt == 1)

        # TC-DB-12  transaction atomicity
        sp = await conn.begin_nested()
        ae = f"{uuid.uuid4()}@t.io"; await new_user(conn, ae)
        await sp.rollback()
        gone = (await conn.execute(text("SELECT count(*) FROM users WHERE email=:e"), {"e": ae})).scalar()
        rec("TC-DB-12", "TRANSACTION: rolled-back insert leaves no row (atomicity)", gone == 0)

        # TC-DB-13  numeric precision
        sp = await conn.begin_nested()
        hid = str(uuid.uuid4())
        await conn.execute(text("INSERT INTO holdings (id,user_id,ticker,quantity,avg_cost) "
            "VALUES (:i,:u,'AAPL',1.2345,123.4567)"), {"i": hid, "u": str(uid)})
        q = (await conn.execute(text("SELECT quantity,avg_cost FROM holdings WHERE id=:i"), {"i": hid})).first()
        await sp.rollback()
        rec("TC-DB-13", f"NUMERIC(18,4): stored {q[0]} / {q[1]} with exact precision",
            float(q[0]) == 1.2345 and float(q[1]) == 123.4567)

        # TC-DB-14  CRUD persistence
        sp = await conn.begin_nested()
        cu = await new_user(conn)
        await conn.execute(text("UPDATE users SET full_name='Updated' WHERE id=:i"), {"i": cu})
        nm = (await conn.execute(text("SELECT full_name FROM users WHERE id=:i"), {"i": cu})).scalar()
        await sp.rollback()
        rec("TC-DB-14", f"CRUD: insert then update reads back new value ('{nm}')", nm == "Updated")

        await outer.rollback()
    await engine.dispose()

    print("=" * 66)
    print("  STOCKPILOT DATABASE TEST SUITE   (PostgreSQL 16, SQLAlchemy async)")
    print("=" * 66)
    for tid, desc, res in results:
        print(f"  {tid:9} {desc:49} {res}")
    print("=" * 66)
    p = sum(1 for _, _, r in results if r == PASS)
    print(f"  {p}/{len(results)} passed   (all writes rolled back - database unchanged)")


if __name__ == "__main__":
    asyncio.run(main())
