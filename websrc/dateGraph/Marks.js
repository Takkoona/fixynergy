import React from "react";
import { line } from "d3";

export function DotMarks({
    groupedData,
    xScale,
    xValue,
    xAxisTickFormat,
    yScale,
    yValue,
    colorScale,
    innerHeigth
}) {
    return Array.from(groupedData).map(([mut, data]) => {
        const linePath = line().x(d => xScale(xValue(d))).y(d => innerHeigth - yScale(yValue(d)));
        data = data.sort((a, b) => xValue(a) - xValue(b));
        return (
            <g key={mut}>
                <path
                    key={mut + "line"}
                    fill="none"
                    stroke={colorScale(mut)}
                    d={linePath(data)}
                ></path>
                {data.map(d => (
                    <circle
                        key={`${d["mut"]}${xAxisTickFormat(xValue(d))}`}
                        cx={xScale(xValue(d))}
                        cy={innerHeigth - yScale(yValue(d))}
                        r="2"
                        fill={colorScale(mut)}
                    ></circle>
                ))}
            </g>
        )
    });
}
