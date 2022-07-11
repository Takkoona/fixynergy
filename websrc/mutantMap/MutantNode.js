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
        if (mutSetNode.ratioSum === 0) {
            return undefined;
        }
        return (
            <g key={mutSetId}>
                <circle
                    key={mutSetId.toString() + "node"}
                    cx={x}
                    cy={y}
                    r={nodeSizeScale(mutSetNode.ratioSum)}
                    fill="yellow"
                    opacity="0.2"
                    stroke="red"
                    strokeWidth="2"
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
                            stroke="red"
                        >
                            <title>{`Mutation: ${mutationName(...mut)}`}</title>
                        </line>
                    );
                })}
            </g>
        )
    });
};
