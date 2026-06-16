// frontend/src/components/auth/Register.jsx
import React, { useState, useRef } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import styles from './Register.module.css'; 


const Register = () => {
  const navigate = useNavigate();

  // State variables
  const [formData, setFormData] = useState({
    fullName: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [termsAccepted, setTermsAccepted] = useState(false);
  const [errors, setErrors] = useState({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  // Password visibility toggle
  const [showPassword, setShowPassword] = useState(false);
  const togglePasswordVisibility = () => setShowPassword(!showPassword);

  // Refs for input wrappers (for styling)
  const nameWrapRef = useRef(null);
  const emailWrapRef = useRef(null);
  const pwWrapRef = useRef(null);
  const cpwWrapRef = useRef(null);

  // Password strength
  const getStrength = (pw) => {
    let score = 0;
    if (pw.length >= 8) score++;
    if (pw.length >= 12) score++;
    if (/[a-z]/.test(pw) && /[A-Z]/.test(pw)) score++;
    if (/\d/.test(pw)) score++;
    if (/[^a-zA-Z0-9]/.test(pw)) score++;
    return Math.min(score, 4);
  };

  const passwordStrength = getStrength(formData.password);
  const strengthLabel = passwordStrength === 0 ? '—' :
    passwordStrength <= 2 ? 'Weak' :
    passwordStrength === 3 ? 'Medium' : 'Strong';

  // Validation functions
  const validateName = () => {
    const val = formData.fullName.trim();
    if (val.length < 2) {
      setErrors(prev => ({ ...prev, fullName: 'Please enter your full name (min 2 characters).' }));
      return false;
    }
    setErrors(prev => ({ ...prev, fullName: '' }));
    return true;
  };

  const validateEmail = () => {
    const val = formData.email.trim();
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!val) {
      setErrors(prev => ({ ...prev, email: 'Email address is required.' }));
      return false;
    }
    if (!re.test(val)) {
      setErrors(prev => ({ ...prev, email: 'Please enter a valid email address.' }));
      return false;
    }
    setErrors(prev => ({ ...prev, email: '' }));
    return true;
  };

  const validatePassword = () => {
    const val = formData.password;
    if (val.length < 8) {
      setErrors(prev => ({ ...prev, password: 'Password must be at least 8 characters.' }));
      return false;
    }
    if (!/[a-zA-Z]/.test(val) || !/\d/.test(val)) {
      setErrors(prev => ({ ...prev, password: 'Include at least one letter and one number.' }));
      return false;
    }
    setErrors(prev => ({ ...prev, password: '' }));
    return true;
  };

  const validateConfirm = () => {
    const pw = formData.password;
    const cpw = formData.confirmPassword;
    if (!cpw) {
      setErrors(prev => ({ ...prev, confirmPassword: 'Please confirm your password.' }));
      return false;
    }
    if (pw !== cpw) {
      setErrors(prev => ({ ...prev, confirmPassword: 'Passwords do not match.' }));
      return false;
    }
    setErrors(prev => ({ ...prev, confirmPassword: '' }));
    return true;
  };

  const validateTerms = () => {
    if (!termsAccepted) {
      setErrors(prev => ({ ...prev, terms: 'You must agree to the Terms and Privacy Policy.' }));
      return false;
    }
    setErrors(prev => ({ ...prev, terms: '' }));
    return true;
  };

  // Handle input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    // Clear field error on change
    setErrors(prev => ({ ...prev, [name]: '' }));
  };

  const handleTermsChange = (e) => {
    setTermsAccepted(e.target.checked);
    if (e.target.checked) {
      setErrors(prev => ({ ...prev, terms: '' }));
    }
  };

  // Handle submit
  const handleSubmit = async (e) => {
    e.preventDefault();

    // Run all validators
    const isNameValid = validateName();
    const isEmailValid = validateEmail();
    const isPwValid = validatePassword();
    const isConfirmValid = validateConfirm();
    const isTermsValid = validateTerms();

    if (isNameValid && isEmailValid && isPwValid && isConfirmValid && isTermsValid) {
      setIsSubmitting(true);
      // Simulate API call
      try {
        // Replace with actual API call: await api.register(formData);
        await new Promise(resolve => setTimeout(resolve, 1800));
        setSubmitSuccess(true);
        setIsSubmitting(false);
        // Optionally redirect after success
        // navigate('/dashboard');
      } catch (error) {
        console.error('Registration error:', error);
        setIsSubmitting(false);
        setErrors(prev => ({ ...prev, form: 'Registration failed. Please try again.' }));
      }
    } else {
      // Focus first field with error
      const firstErrorField = document.querySelector('.input-wrap.error input');
      if (firstErrorField) firstErrorField.focus();
    }
  };

  // Render
  return (
    <div className={styles['auth-wrapper']}>
      <div className={styles['auth-card']}>
        {/* Logo */}
        <Link to="/" className={styles['auth-logo']}>
          <div className={styles['mark']}>$$</div>
          Stock<span>Sense</span>
        </Link>
        <div className={styles['auth-sub']}>AI Investment Advisor · Final Year Project</div>

        <h1 className={styles['auth-heading']}>
          Create <em>Account</em>
        </h1>
        <p className={styles['auth-description']}>
          Start building your AI-powered portfolio.
        </p>

        <form className={styles['auth-form']} onSubmit={handleSubmit} noValidate>
          {/* Full Name */}
          <div className={styles['form-group']}>
            <label>
              <i className="fas fa-user"></i> Full Name <span className={styles['req']}>*</span>
            </label>
            <div className={`${styles['input-wrap']} ${errors.fullName ? styles.error : ''} ${formData.fullName && !errors.fullName ? styles.success : ''}`} ref={nameWrapRef}>
              <span className={styles['icon']}><i className="fas fa-user"></i></span>
              <input
                type="text"
                name="fullName"
                value={formData.fullName}
                onChange={handleChange}
                onBlur={validateName}
                placeholder="e.g. Alex Rivera"
                autoComplete="name"
                required
              />
            </div>
            {errors.fullName && <div className={styles['form-error']}>{errors.fullName}</div>}
          </div>

          {/* Email */}
          <div className={styles['form-group']}>
            <label>
              <i className="fas fa-envelope"></i> Email Address <span className={styles['req']}>*</span>
            </label>
            <div className={`${styles['input-wrap']} ${errors.email ? styles.error : ''} ${formData.email && !errors.email ? styles.success : ''}`} ref={emailWrapRef}>
              <span className={styles['icon']}><i className="fas fa-envelope"></i></span>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={validateEmail}
                placeholder="you@example.com"
                autoComplete="email"
                required
              />
            </div>
            {errors.email && <div className={styles['form-error']}>{errors.email}</div>}
          </div>

          {/* Password */}
          <div className={styles['form-group']}>
            <label>
              <i className="fas fa-lock"></i> Password <span className={styles['req']}>*</span>
            </label>
            <div className={`${styles['input-wrap']} ${errors.password ? styles.error : ''} ${formData.password && !errors.password ? styles.success : ''}`} ref={pwWrapRef}>
              <span className={styles['icon']}><i className="fas fa-lock"></i></span>
              <input
                type={showPassword ? 'text' : 'password'}
                name="password"
                value={formData.password}
                onChange={handleChange}
                onBlur={validatePassword}
                placeholder="Min 8 characters"
                autoComplete="new-password"
                required
              />
              <button type="button" className={styles['toggle-pw']} onClick={togglePasswordVisibility} aria-label="Toggle password visibility">
                <i className={`fas ${showPassword ? 'fa-eye-slash' : 'fa-eye'}`}></i>
              </button>
            </div>
            {/* Password strength */}
            <div className={styles['pw-strength']}>
              <div className={styles['bars']}>
                {[1, 2, 3, 4].map(i => (
                  <span
                    key={i}
                    className={`${styles['bar']} ${i <= passwordStrength ? styles['active'] : ''} 
                      ${i <= passwordStrength && (passwordStrength <= 2 ? styles['weak'] : passwordStrength === 3 ? styles['medium'] : styles['strong'])}`}
                  ></span>
                ))}
              </div>
              <span className={`${styles['label']} ${strengthLabel !== '—' ? styles[strengthLabel.toLowerCase()] : ''}`}>
                {strengthLabel}
              </span>
            </div>
            {errors.password && <div className={styles['form-error']}>{errors.password}</div>}
          </div>

          {/* Confirm Password */}
          <div className={styles['form-group']}>
            <label>
              <i className="fas fa-check-circle"></i> Confirm Password <span className={styles['req']}>*</span>
            </label>
            <div className={`${styles['input-wrap']} ${errors.confirmPassword ? styles.error : ''} ${formData.confirmPassword && !errors.confirmPassword ? styles.success : ''}`} ref={cpwWrapRef}>
              <span className={styles['icon']}><i className="fas fa-check-circle"></i></span>
              <input
                type={showPassword ? 'text' : 'password'}
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                onBlur={validateConfirm}
                placeholder="Re-enter your password"
                autoComplete="new-password"
                required
              />
            </div>
            {errors.confirmPassword && <div className={styles['form-error']}>{errors.confirmPassword}</div>}
          </div>

          {/* Terms */}
          <div className={styles['terms-group']}>
            <input
              type="checkbox"
              id="terms"
              checked={termsAccepted}
              onChange={handleTermsChange}
            />
            <label htmlFor="terms">
              I agree to the <Link to="/terms">Terms of Service</Link> and <Link to="/privacy">Privacy Policy</Link>.
            </label>
          </div>
          {errors.terms && <div className={styles['form-error']} style={{ paddingLeft: '28px' }}>{errors.terms}</div>}

          {/* Submit */}
          <button type="submit" className={styles['btn-submit']} disabled={isSubmitting || submitSuccess}>
            {isSubmitting ? (
              <>
                <span className={styles['spinner']}></span> Creating…
              </>
            ) : submitSuccess ? (
              '✓ Account Created!'
            ) : (
              <>
                Create Account <i className="fas fa-arrow-right"></i>
              </>
            )}
          </button>

          {/* Divider */}
          <div className={styles['auth-divider']}>
            <span>or continue with</span>
          </div>

          {/* Social buttons */}
          <div className={styles['social-row']}>
            <button type="button" className={`${styles['btn-social']} ${styles['google']}`}>
              <i className="fab fa-google"></i> Google
            </button>
            <button type="button" className={`${styles['btn-social']} ${styles['github']}`}>
              <i className="fab fa-github"></i> GitHub
            </button>
          </div>
        </form>

        <div className={styles['auth-footer']}>
          Already have an account? <Link to="/login">Sign in</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;