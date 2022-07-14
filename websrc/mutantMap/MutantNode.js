import React from "react";
import { max, pie, arc } from "d3";
import { mutationName } from "../utils";
import { setMutOpacity } from "../utils";

export function MutantNode({
    landscapeData,
    mutColorScale,
    xScale,
    yScales,
    nodeSizeScale,
    hoveredMut
}) {
    return Array.from(landscapeData).map(([mutSetId, mutSetNode]) => {
        const [x, y] = mutSetNode.setCoord(xScale, yScales).getCoord();
        if (mutSetNode.ratioSum === 0) {
            return undefined;
        }
        const mutIncreValues = [];
        const pieRadius = nodeSizeScale(mutSetNode.ratioSum);
        const arcScale = arc().innerRadius(0).outerRadius(pieRadius);
        const pieScale = pie().value(d => d["ratioDiff"]);
        return (
            <g key={mutSetId}>
                {mutSetNode.parentLinks.map(([parent, mut]) => {
                    const mutName = mutationName(...mut);
                    const ratioDiff = mutSetNode.ratioSum - parent.ratioSum;
                    mutIncreValues.push({ mutName, ratioDiff });
                    return (
                        <line
                            key={[mutSetId, parent.id].join(",")}
                            x1={parent.x}
                            y1={parent.y}
                            x2={x}
                            y2={y}
                            strokeWidth="1"
                            opacity={setMutOpacity(hoveredMut, mutName, 0, max([ratioDiff, 0]))}
                            stroke={mutColorScale(mutName)}
                        >
                            <title>{`Mutation: ${mutName}`}</title>
                        </line>
                    );
                })}
                <g transform={`translate(${x}, ${y})`}>
                    {pieScale(mutIncreValues).map(({
                        data,
                        startAngle,
                        endAngle
                    }) => {
                        const mutName = data["mutName"];
                        const pieArcColor = mutColorScale(mutName);
                        const arcPathGen = arcScale.startAngle(startAngle).endAngle(endAngle);
                        return (
                            <path
                                key={`${mutSetId}${mutName}_pie`}
                                d={arcPathGen()}
                                fill={pieArcColor}
                                fillOpacity={setMutOpacity(hoveredMut, mutName, 0.05, 0.5)}
                                stroke={pieArcColor}
                                strokeOpacity={setMutOpacity(hoveredMut, mutName)}
                            >
                                <title>{data["mutName"]}</title>
                            </path>
                        )
                    })}
                </g>
                <circle
                    key={mutSetId.toString() + "node"}
                    cx={x}
                    cy={y}
                    r={pieRadius}
                    fill="none"
                    stroke="#d3d3d3"
                    strokeWidth="1"
                >
                    <title>{mutSetNode.getMutName()}</title>
                </circle>
            </g>
        );
    });
};
