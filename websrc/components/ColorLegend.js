import React from "react";
import { setMutOpacity } from "../utils";

const tickSpacing = 20;
const tickSize = 5;

export function ColorLegend({ mutColorScale, hoveredMut, setHoveredMut }) {
    return mutColorScale.domain().map((mutName, i) => {
        return (
            <g
                key={`${mutName}_legend`}
                transform={`translate(0, ${i * tickSpacing})`}
                onMouseEnter={() => { setHoveredMut(mutName); }}
                onMouseOut={() => { setHoveredMut(null); }}
                opacity={setMutOpacity(hoveredMut, mutName)}
            >
                <circle fill={mutColorScale(mutName)} r={tickSize}></circle>
                <text x={10} fontSize={10} dy="0.32em">{mutName}</text>
            </g>
        );
    });
};
