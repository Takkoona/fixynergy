import React from "react";
import { timeFormat, scaleTime, scaleLinear } from "d3";
import { AxisBottom, AxisLeft } from "./Axses";
import { DotMarks } from "./Marks";

const margin = { top: 10, right: 200, bottom: 20, left: 30 };

const xValue = d => d["date"];
const xAxisTickFormat = timeFormat('%m/%d/%Y');
const xTickOffset = 10;

const yValue = d => d["ratio"];
const yTickOffset = 10;

export function DateGraph({
    mutDailyFreq,
    mutColorScale,
    dateRange,
    width,
    height,
    hoveredMut
}) {

    const innerWidth = width - margin.left - margin.right;
    const innerHeight = height - margin.top - margin.bottom;

    const xScale = scaleTime().domain(dateRange).range([0, innerWidth]).nice();
    const yScale = scaleLinear().domain([0, 1]).range([innerHeight, 0]);

    return (
        <g transform={`translate(${margin.left}, ${margin.top})`}>
            <DotMarks
                groupedData={mutDailyFreq}
                xScale={xScale}
                xValue={xValue}
                xAxisTickFormat={xAxisTickFormat}
                yScale={yScale}
                yValue={yValue}
                colorScale={mutColorScale}
                innerHeigth={innerHeight}
                hoveredMut={hoveredMut}
            ></DotMarks>
            <AxisBottom
                xScale={xScale}
                xAxisTickFormat={xAxisTickFormat}
                innerHeight={innerHeight}
                tickOffset={xTickOffset}
            ></AxisBottom>
            <AxisLeft
                yScale={yScale}
                innerWidth={innerWidth}
                tickOffset={yTickOffset}
            ></AxisLeft>
        </g>
    );
};
