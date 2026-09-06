import { useEffect, useRef, useState } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip
} from "recharts";

function RainfallChart({ data = [] }) {
  const containerRef = useRef(null);
  const [width, setWidth] = useState(700);

  useEffect(() => {
    const element = containerRef.current;

    if (!element) return;

    const updateWidth = () => {
      const newWidth = element.clientWidth;

      if (newWidth > 0) {
        setWidth(newWidth);
      }
    };

    updateWidth();

    const observer = new ResizeObserver(updateWidth);
    observer.observe(element);

    return () => observer.disconnect();
  }, []);

  const chartData = data.map((item, index) => ({
    time: item?.time || `${index + 1}`,
    rainfall: Number(item?.rainfall) || 0
  }));

  return (
    <div className="chart-card rainfall-chart-card">

      <div className="section-title">
        <div>
          <h2>Rainfall Trend</h2>
          <p>Last 24 hours</p>
        </div>
      </div>

      <div
        ref={containerRef}
        className="rainfall-chart-container"
        style={{
          width: "100%",
          height: "300px"
        }}
      >
        {chartData.length > 0 ? (

          <LineChart
            width={width}
            height={300}
            data={chartData}
            margin={{
              top: 10,
              right: 20,
              left: 0,
              bottom: 10
            }}
          >

            <CartesianGrid
              stroke="#e2e8f0"
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="time"
              tick={{
                fontSize: 12,
                fill: "#64748b"
              }}
            />

            <YAxis
              tick={{
                fontSize: 12,
                fill: "#64748b"
              }}
              width={45}
              domain={[0, "auto"]}
            />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="rainfall"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{
                r: 3,
                fill: "#2563eb"
              }}
              activeDot={{
                r: 6
              }}
              connectNulls
              isAnimationActive={false}
            />

          </LineChart>

        ) : (

          <div className="chart-empty">
            <span>No rainfall data available</span>
          </div>

        )}
      </div>

    </div>
  );
}

export default RainfallChart;