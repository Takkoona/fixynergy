import React from "react";
import { scaleLinear, scaleSqrt } from "d3";
import { MutantNode } from "./MutantNode";

const margin = { top: 40, right: 40, bottom: 40, left: 40 }
const maxNodeSize = 100;

export function MutantMap({
    landscapeData,
    laneLengths,
    laneExist,
    mutColorScale,
    maxRatioSum,
    width,
    height
}) {

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const yScales = laneLengths.map(l => {
        return scaleLinear().domain([0, l + 1]).range([innerHeight, 0])
    });

    let startIndex = 0;
    let endIndex = laneExist.length - 1;
    for (; startIndex < endIndex; startIndex++) {
        if (laneExist[startIndex]) { break; }
    };
    for (; endIndex >= startIndex; endIndex--) {
        if (laneExist[endIndex]) { break; }
    };
    laneLengths = laneLengths.slice(startIndex, endIndex);
    const xScale = scaleLinear().domain([0, laneLengths.length]).range([0, innerWidth]);

    const nodeSizeScale = scaleSqrt().domain([0, maxRatioSum]).range([0, maxNodeSize]);

    return (
        <g transform={`translate(${margin.left}, ${margin.top})`}>
            <MutantNode
                landscapeData={landscapeData}
                mutColorScale={mutColorScale}
                xScale={xScale}
                yScales={yScales}
                nodeSizeScale={nodeSizeScale}
            ></MutantNode>
        </g>
    );
};
