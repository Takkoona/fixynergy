import React from "react";
import { max } from "d3";
import { mutationName } from "../utils";

export function MutantNode({
    landscapeData,
    mutColorScale,
    xScale,
    yScales,
    nodeSizeScale
}) {
    return Array.from(landscapeData).map(([mutSetId, mutSetNode]) => {
        const [x, y] = mutSetNode.setCoord(xScale, yScales).getCoord();
        if (mutSetNode.ratioSum === 0) {
            return undefined;
        }
        let minRatioSum = Infinity;
        let nodeStrokeColor = "grey";
        let maxIncreMut = null;
        return (
            <g key={mutSetId}>
                {mutSetNode.parentLinks.map(([parent, mut]) => {
                    const mutName = mutationName(...mut);
                    const currRatioSum = parent.ratioSum;
                    if (currRatioSum < minRatioSum) {
                        minRatioSum = currRatioSum;
                        maxIncreMut = mutName;
                        nodeStrokeColor = mutColorScale(maxIncreMut);
                    }
                    const ratioDiff = mutSetNode.ratioSum - parent.ratioSum;
                    return (
                        <line
                            key={[mutSetId, parent.id].join(",")}
                            x1={parent.x}
                            y1={parent.y}
                            x2={x}
                            y2={y}
                            strokeWidth="1"
                            opacity={max([ratioDiff, 0])}
                            // opacity={1}
                            stroke={mutColorScale(mutName)}
                        >
                            <title>{`Mutation: ${mutName}`}</title>
                        </line>
                    );
                })}
                <circle
                    key={mutSetId.toString() + "node"}
                    cx={x}
                    cy={y}
                    r={nodeSizeScale(mutSetNode.ratioSum)}
                    fill={nodeStrokeColor}
                    fillOpacity="0.5"
                    stroke={nodeStrokeColor}
                    strokeWidth="1"
                >
                    <title>{mutSetNode.getMutName()}</title>
                </circle>
            </g>
        )
    });
};
