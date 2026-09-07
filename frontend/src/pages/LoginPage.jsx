import React, { useState } from "react";
import "./LoginPage.css";

/* ---------- Small inline icons ---------- */

function Icon({ name, size = 17 }) {
  const common = {
    width: size,
    height: size,
    viewBox: "0 0 24 24",
    fill: "none",
    stroke: "currentColor",
    strokeWidth: 1.8,
    strokeLinecap: "round",
    strokeLinejoin: "round",
    "aria-hidden": true,
  };

  const paths = {
    shield: (
      <>
        <path d="M12 3 20 6v5c0 5-3.3 8.7-8 10-4.7-1.3-8-5-8-10V6l8-3Z" />
        <path d="m9 12 2 2 4-4" />
      </>
    ),
    user: (
      <>
        <circle cx="12" cy="8" r="3" />
        <path d="M5.5 20c.7-3.2 2.8-5 6.5-5s5.8 1.8 6.5 5" />
      </>
    ),
    userPlus: (
      <>
        <circle cx="9" cy="8" r="3" />
        <path d="M2.8 20c.7-3.2 2.8-5 6.2-5 2 0 3.6.5 4.8 1.5" />
        <path d="M17 8v6M14 11h6" />
      </>
    ),
    mail: (
      <>
        <rect x="3" y="5" width="18" height="14" rx="2" />
        <path d="m4 7 8 6 8-6" />
      </>
    ),
    lock: (
      <>
        <rect x="4.5" y="10" width="15" height="10" rx="2" />
        <path d="M8 10V7.5a4 4 0 0 1 8 0V10M12 14v2" />
      </>
    ),
    eye: (
      <>
        <path d="M2.5 12s3.2-6 9.5-6 9.5 6 9.5 6-3.2 6-9.5 6-9.5-6-9.5-6Z" />
        <circle cx="12" cy="12" r="2.4" />
      </>
    ),
    eyeOff: (
      <>
        <path d="m3 3 18 18" />
        <path d="M10.6 10.6a2 2 0 0 0 2.8 2.8" />
        <path d="M9.9 4.3A10.8 10.8 0 0 1 12 4c5.2 0 8.7 4.2 9.5 6-.4.9-1.5 2.4-3.1 3.7M6.4 6.4C4.5 7.7 3.3 9.3 2.5 10c.8 1.8 4.3 6 9.5 6 1 0 2-.2 2.9-.5" />
      </>
    ),
    arrow: <path d="M5 12h13m-5-5 5 5-5 5" />,
    menu: (
      <>
        <path d="M4 7h16M4 12h16M4 17h16" />
      </>
    ),
  };

  return <svg {...common}>{paths[name]}</svg>;
}


/* ---------- Brand ---------- */

function Brand() {
  return (
    <div className="brand">
      <div className="brand-mark">
        <Icon name="shield" size={18} />
      </div>

      <div className="brand-copy">
        <strong>MPLADS</strong>
        <span>RISK INTELLIGENCE</span>
      </div>
    </div>
  );
}


/* ---------- Hero illustration ----------
   Everything below is CSS/SVG/HTML. No external image is required.
*/

function IndiaMap() {
  return (
    <svg className="india-map" viewBox="0 0 390 410" aria-hidden="true">
      <path
        className="india-fill"
        d="M135 13 181 26l20 29 40 13 14 30 36 18-10 33 29 29-17 30 11 31-22 25-10 39-29 23-20 36-25-9-17-35-30-11-8-33-32-20 5-32-27-25 19-28-8-30 29-25-4-33 21-22 10-35 25-23Z"
      />
      <g className="map-lines">
        <path d="M135 14 164 51l-14 38 19 31-14 31 25 31-8 34 29 26-13 43" />
        <path d="M201 55 188 93l37 25-9 33 35 22" />
        <path d="m96 121 40 8 31-21 32 12 34-9" />
        <path d="m108 199 39-13 25 26 45-8 23 22" />
        <path d="m121 262 44-8 19 29 43 8" />
        <path d="m156 323 25-31 38 13 14-33" />
      </g>
    </svg>
  );
}

function Pin({ left, top, delay = "0s" }) {
  return (
    <span
      className="map-pin"
      style={{ left: `${left}%`, top: `${top}%`, animationDelay: delay }}
    />
  );
}

function MiniChart() {
  return (
    <div className="mini-chart" aria-hidden="true">
      <div className="chart-bars">
        <i />
        <i />
        <i />
      </div>
      <div className="chart-line" />
    </div>
  );
}

function PaperPlane({ className = "" }) {
  return (
    <svg className={`paper-plane ${className}`} viewBox="0 0 80 60">
      <path d="M7 31 69 5 48 52 35 36 7 31Z" />
      <path d="m35 36 13-26" />
    </svg>
  );
}

function LaptopArtwork() {
  return (
    <div className="laptop-scene" aria-hidden="true">
      <div className="person">
        <div className="person-hair-back" />
        <div className="person-neck" />
        <div className="person-head" />
        <div className="person-hair" />
        <div className="person-body" />
        <div className="person-arm" />
      </div>

      <div className="laptop">
        <div className="laptop-screen">
          <div className="screen-top">
            <b>MPLADS</b>
            <span />
          </div>
          <div className="screen-content">
            <div className="screen-map" />
            <div className="screen-chart">
              <i />
              <i />
              <i />
            </div>
            <div className="screen-text">
              <i />
              <i />
              <i />
            </div>
          </div>
        </div>
        <div className="laptop-base" />
      </div>

      <div className="books">
        <i />
        <i />
        <i />
      </div>

      <div className="plant">
        <span className="leaf leaf-a" />
        <span className="leaf leaf-b" />
        <span className="leaf leaf-c" />
        <span className="leaf leaf-d" />
        <span className="pot" />
      </div>
    </div>
  );
}

function HeroArtwork() {
  return (
    <div className="hero-art" aria-hidden="true">
      <div className="art-glow glow-one" />
      <div className="art-glow glow-two" />

      <IndiaMap />

      <div className="map-pins">
        <Pin left={47} top={28} delay="0s" />
        <Pin left={61} top={35} delay=".25s" />
        <Pin left={52} top={49} delay=".5s" />
        <Pin left={68} top={54} delay=".75s" />
        <Pin left={58} top={66} delay="1s" />
      </div>

      <div className="chart-card">
        <MiniChart />
      </div>

      <svg className="dashed-path path-a" viewBox="0 0 330 130">
        <path d="M8 94C63 18 112 110 168 57S265 20 318 60" />
      </svg>

      <svg className="dashed-path path-b" viewBox="0 0 250 120">
        <path d="M8 94C55 49 75 111 122 70S193 23 241 55" />
      </svg>

      <PaperPlane className="plane-a" />
      <PaperPlane className="plane-b" />

      <LaptopArtwork />

      <span className="spark spark-a">✧</span>
      <span className="spark spark-b">✦</span>
    </div>
  );
}


/* ---------- Login page ---------- */

export default function LoginPage({ onLogin, onSignUp }) {
  const [mode, setMode] = useState("signin");
  const [loginId, setLoginId] = useState("");
  const [password, setPassword] = useState("");
  const [remember, setRemember] = useState(true);
  const [showPassword, setShowPassword] = useState(false);

  const submit = (event) => {
    event.preventDefault();

    if (mode === "signup") {
      onSignUp?.({ loginId, password });
    } else {
      onLogin?.({ loginId, password, remember });
    }
  };

  return (
    <main className="mplads-login-page">
      <div className="login-shell">
        {/* Hero / branding */}
        <section className="hero-panel">
          <Brand />

          <button className="mobile-menu" type="button" aria-label="Open menu">
            <Icon name="menu" size={18} />
          </button>

          <div className="hero-copy">
            <h1>
              Smarter Insights.
              <br />
              Safer Projects.
            </h1>

            <p>
              AI-powered risk analysis for better planning and transparent
              MPLADS implementation.
            </p>
          </div>

          <HeroArtwork />
        </section>

        {/* Auth */}
        <section className="auth-panel">
          <div className="auth-card">
            <div className="auth-title">
              <h2>Welcome Back</h2>
              <p>Sign in to access the MPLADS Risk Intelligence portal.</p>
            </div>

            <div className="auth-tabs" role="tablist">
              <button
                type="button"
                role="tab"
                aria-selected={mode === "signin"}
                className={mode === "signin" ? "active" : ""}
                onClick={() => setMode("signin")}
              >
                <Icon name="user" size={16} />
                Sign In
              </button>

              <button
                type="button"
                role="tab"
                aria-selected={mode === "signup"}
                className={mode === "signup" ? "active" : ""}
                onClick={() => setMode("signup")}
              >
                <Icon name="userPlus" size={16} />
                Sign Up
              </button>
            </div>

            <form className="auth-form" onSubmit={submit}>
              <label htmlFor="login-id">Login ID</label>

              <div className="field">
                <Icon name="user" size={16} />
                <input
                  id="login-id"
                  value={loginId}
                  onChange={(e) => setLoginId(e.target.value)}
                  type="text"
                  placeholder="Enter your login ID"
                  autoComplete="username"
                  required
                />
              </div>

              <label htmlFor="login-password">Password</label>

              <div className="field">
                <Icon name="lock" size={16} />
                <input
                  id="login-password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  type={showPassword ? "text" : "password"}
                  placeholder="Enter your password"
                  autoComplete={
                    mode === "signin" ? "current-password" : "new-password"
                  }
                  required
                />

                <button
                  className="eye-button"
                  type="button"
                  onClick={() => setShowPassword((v) => !v)}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  <Icon
                    name={showPassword ? "eyeOff" : "eye"}
                    size={15}
                  />
                </button>
              </div>

              {mode === "signin" && (
                <div className="form-row">
                  <label className="remember">
                    <input
                      type="checkbox"
                      checked={remember}
                      onChange={(e) => setRemember(e.target.checked)}
                    />
                    <span className="checkmark">✓</span>
                    <span>Remember me</span>
                  </label>

                  <button
                    type="button"
                    className="forgot"
                    onClick={() =>
                      alert(
                        "Please contact your administrator to reset your password."
                      )
                    }
                  >
                    Forgot password?
                  </button>
                </div>
              )}

              <button className="submit" type="submit">
                {mode === "signin" ? "Sign In" : "Create Account"}
                <Icon name="arrow" size={15} />
              </button>
            </form>

            <div className="auth-footer">
              {mode === "signin" ? (
                <>
                  <span>Don&apos;t have an account?</span>
                  <button type="button" onClick={() => setMode("signup")}>
                    Create your account
                  </button>
                </>
              ) : (
                <>
                  <span>Already have an account?</span>
                  <button type="button" onClick={() => setMode("signin")}>
                    Sign in
                  </button>
                </>
              )}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
