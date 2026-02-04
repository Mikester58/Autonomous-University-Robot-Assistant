import { useAuth } from "../services/authService";
import "../styles/login.css";

export default function LoginPage() {
    const { login } = useAuth();

    const handleSubmit = (e: React.FormEvent) => {
        e.preventDefault();
        login();
    };

    return (
        <div className="login-container">
            <div className="login-box">
                <h2>ARUA Login</h2>

                <form onSubmit={handleSubmit}>
                    <button type="submit" className="login-btn">
                        Login as Student
                    </button>
                </form>
            </div>
        </div>
    );
}
