import React from "react";
import {
    group,
    extent,
    timeFormat,
    scaleTime,
    scaleLinear,
    scaleOrdinal,
    schemeSet3
} from "d3";
import { AxisBottom, AxisLeft } from "./Axses";
import { DotMarks } from "./Marks";

const margin = { top: 20, right: 20, bottom: 20, left: 20 };

const xValue = d => d["date"];
const xAxisTickFormat = timeFormat('%m/%d/%Y');
const xTickOffset = 20;
const xAxisLabel = "Collection Date";

const yValue = d => d["ratio"];
const yTickOffset = 1;
const yAxisLabel = "Mutation Ratio";

export function DateGraph({ dailyMutFreq, width, height }) {

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const xScale = scaleTime().domain(extent(dailyMutFreq, xValue)).range([0, innerWidth]).nice();
    const yScale = scaleLinear().domain([0, 1]).range([innerHeight, 0]);

    const groupedData = group(dailyMutFreq, d => d["mut"])
    const colorScale = scaleOrdinal().domain(groupedData.keys()).range(schemeSet3);

    return (
        <>
            <g transform={`translate(${margin.left}, ${margin.top})`}>
                <DotMarks
                    groupedData={groupedData}
                    xScale={xScale}
                    xValue={xValue}
                    xAxisTickFormat={xAxisTickFormat}
                    yScale={yScale}
                    yValue={yValue}
                    colorScale={colorScale}
                    innerHeigth={innerHeight}
                ></DotMarks>
                <AxisBottom
                    xScale={xScale}
                    innerHeight={innerHeight}
                    xAxisTickFormat={xAxisTickFormat}
                    tickOffset={xTickOffset}
                ></AxisBottom>
                <AxisLeft
                    yScale={yScale}
                    innerWidth={innerWidth}
                    tickOffset={yTickOffset}
                ></AxisLeft>
            </g>
        </>
    );
}
