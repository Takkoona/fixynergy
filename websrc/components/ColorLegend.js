import React from "react";
import { setMutOpacity } from "../utils";

const tickSpacing = 20;
const tickSize = 5;

export function ColorLegend({
    mutColorScale,
    hoveredMut,
    setHoveredMut,
    selectedMuts,
    setSelectedMuts
}) {
    return mutColorScale.domain().map((mutName, i) => {
        return (
            <g
                key={`${mutName}_legend`}
                transform={`translate(0, ${i * tickSpacing})`}
                onMouseEnter={() => { setHoveredMut(mutName); }}
                onMouseOut={() => { setHoveredMut(null); }}
                onClick={() => {
                    setSelectedMuts(prevSelectedMut => {
                        const mutNameIndex = prevSelectedMut.indexOf(mutName);
                        if (mutNameIndex === -1) {
                            prevSelectedMut.push(mutName);
                        } else {
                            prevSelectedMut.splice(mutNameIndex, 1);
                        };
                        return prevSelectedMut;
                    });
                }}
                opacity={setMutOpacity(hoveredMut, mutName, selectedMuts)}
            >
                <circle fill={mutColorScale(mutName)} r={tickSize}></circle>
                <text x={10} fontSize={10} dy="0.32em">{mutName}</text>
            </g>
        );
    });
};
