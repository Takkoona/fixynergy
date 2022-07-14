import React from "react";
import { line } from "d3";
import { setMutOpacity } from "../utils";

export function DotMarks({
    groupedData,
    xScale,
    xValue,
    xAxisTickFormat,
    yScale,
    yValue,
    colorScale,
    hoveredMut
}) {
    return Array.from(groupedData).map(([mut, data]) => {
        const linePath = line().x(d => xScale(xValue(d))).y(d => yScale(yValue(d)));
        data = data.sort((a, b) => xValue(a) - xValue(b));
        return (
            <g
                key={mut}
                onMouseEnter={() => { setHoveredMut(mut); }}
                onMouseOut={() => { setHoveredMut(null); }}
                opacity={setMutOpacity(hoveredMut, mut)}
            >
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
                        cy={yScale(yValue(d))}
                        r="2"
                        fill={colorScale(mut)}
                        opacity={setMutOpacity(hoveredMut, mut)}
                    ></circle>
                ))}
            </g>
        )
    });
}
