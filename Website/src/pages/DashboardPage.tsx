import "../styles/dashboard.css";
import robotImage from "../assets/robot.png";
import FilometricsPanel from "../components/UI/FilometricsPanel";

export default function DashboardPage() {
    return (
        <div className="dashboard-page">
            {/* ARUA ROBOT HEADER */}
            <div className="arua-header">
                <div className="arua-panel">
                    <img src={robotImage} alt="ARUA" className="arua-img" />
                    <div className="arua-text">
                        <h1 className="arua-title">ARUA</h1>
                        <div className="arua-sub">System Overview</div>
                    </div>
                </div>
            </div>

            {/* Filometrics */}
            <div className="dashboard-section">
                <FilometricsPanel />
            </div>

            {/* Your existing cards/components go here */}
            <div className="dashboard-cards">
                {/* Example: put StatusCard components here */}
                {/* <StatusCard title="Battery" value="98%" /> */}
            </div>
        </div>
    );
}
