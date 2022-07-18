import React from "react";
import { sum, scaleLinear, scaleSqrt, max, pie, arc } from "d3";
import { mutationName, setMutOpacity } from "../utils";

const margin = { top: 40, right: 40, bottom: 40, left: 40 }
const maxNodeSize = 100;

export function MutantMap({
    landscapeData,
    mutColorScale,
    maxRatioSum,
    width,
    height,
    hoveredMut
}) {

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    let startIndex, endIndex;
    const yScales = landscapeData.map((laneData, index) => {
        const laneRatioSum = sum(laneData, d => d.ratioSum);
        if (laneRatioSum && startIndex === undefined) {
            startIndex = index;
        };
        if (!laneRatioSum && startIndex !== undefined && endIndex === undefined) {
            endIndex = index;
        };
        return scaleLinear().domain([0, laneData.length + 1]).range([innerHeight, 0])
    });
    const xScale = scaleLinear().domain([startIndex, endIndex]).range([0, innerWidth]);
    const nodeSizeScale = scaleSqrt().domain([0, maxRatioSum]).range([0, maxNodeSize]);

    return (
        <g transform={`translate(${margin.left}, ${margin.top})`}>
            <MutantNode
                landscapeData={landscapeData}
                mutColorScale={mutColorScale}
                xScale={xScale}
                yScales={yScales}
                nodeSizeScale={nodeSizeScale}
                hoveredMut={hoveredMut}
            ></MutantNode>
        </g>
    );
};

function MutantNode({
    landscapeData,
    mutColorScale,
    xScale,
    yScales,
    nodeSizeScale,
    hoveredMut
}) {
    return landscapeData.map((laneData, landIndex) => {
        const yScale = yScales.at(landIndex);
        return laneData.map((mutSetNode, nodeIndex) => {
            const x = xScale(mutSetNode.parentLinks.length);
            const y = yScale(nodeIndex + 1);
            mutSetNode.setCoord(x, y);
            if (mutSetNode.ratioSum === 0) {
                return undefined;
            }
            const mutSetId = mutSetNode.id;
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
    });
};
