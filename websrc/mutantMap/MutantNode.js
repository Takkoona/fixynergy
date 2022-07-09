import React from "react";
import { max } from "d3";
import { mutationName } from "../utils";

export function MutantNode({
    landscapeData,
    xScale,
    yScales,
    lineScale,
    nodeSizeScale
}) {
    return Array.from(landscapeData).map(([mutSetId, mutSetNode]) => {
        const [x, y] = mutSetNode.setCoord(xScale, yScales).getCoord();
        return (
            <g key={mutSetId}>
                <circle
                    key={mutSetId.toString() + "node"}
                    cx={x}
                    cy={y}
                    r={nodeSizeScale(mutSetNode.ratioSum)}
                    fill="red"
                    opacity="0.2"
                >
                    <title>{mutSetNode.getMutName()}</title>
                </circle>
                {mutSetNode.parentLinks.map(([parent, mut]) => {
                    const ratioDiff = lineScale(mutSetNode.ratioSum) - lineScale(parent.ratioSum);
                    return (
                        <line
                            key={[mutSetId, parent.id].join(",")}
                            x1={parent.x}
                            y1={parent.y}
                            x2={x}
                            y2={y}
                            strokeWidth="0.5"
                            opacity={max([ratioDiff, 0])}
                            // opacity="1"
                            stroke="#000"
                        >
                            <title>{`Mutation: ${mutationName(...mut)}`}</title>
                        </line>
                    );
                })}
            </g>
        )
    });
};
