import React from "react";
import { sum, scaleLinear, scaleSqrt } from "d3";
import { MutantNode } from "./MutantNode";

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
