import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Login from '../components/auth/Login';

const AppRouter = () => {
  return (
    <BrowserRouter>
      <Routes>
        {/* All routes go to Login */}
        <Route path="/" element={<Login />} />
        <Route path="*" element={<Login />} />
      </Routes>
    </BrowserRouter>
  );
};

export default AppRouter;