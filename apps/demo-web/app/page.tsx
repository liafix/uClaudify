import goldenPath from "../data/golden-path.json";
import { GoldenDemo } from "../components/golden-demo";

export default function CandidateDemoPage() {
  return <div className="demo-grid"><GoldenDemo data={goldenPath} /></div>;
}
