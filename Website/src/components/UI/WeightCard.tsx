import "../../styles/weightCard.css";

interface WeightCardProps {
    weight: number;
}

export default function WeightCard({ weight }: WeightCardProps) {
    return (
        <div className="weight-card">
            <h3>Weight Sensor</h3>
            <p>{weight} lbs</p>
        </div>
    );
}
