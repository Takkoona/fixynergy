import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { group, scaleOrdinal, schemeSet3 } from "d3";
import { LoadData } from "./loadData";
import { MutantMap } from "./mutantMap";
import { DateGraph } from "./dateGraph";
import { ColorLegend } from "./colorLegend";

const root = document.getElementById("mutantLandscape");

const landscapeSpecs = { h: 0.8, w: 1 };
const dateGraphSpecs = { h: 1 - landscapeSpecs.h, w: 1 };

const App = () => {

    const [width, setWidth] = useState(root.offsetWidth);
    const [height, setHeight] = useState(root.offsetHeight);

    const handleResize = () => {
        setWidth(root.offsetWidth);
        setHeight(root.offsetHeight);
    }

    useEffect(() => {
        window.addEventListener("resize", handleResize);
        return () => {
            window.removeEventListener("resize", handleResize);
        }
    }, [])

    const data = LoadData();
    if (!data) return <pre>Loading...</pre>
    const [
        landscapeData,
        laneLengths,
        laneExist,
        dailyMutFreq,
        maxRatioSum,
        dateRange
    ] = data;

    const mutDailyFreq = group(dailyMutFreq, d => d["mut"]);
    const mutColorScale = scaleOrdinal().domain(mutDailyFreq.keys()).range(schemeSet3);

    return (
        <svg width={width} height={height}>
            <DateGraph
                mutDailyFreq={mutDailyFreq}
                mutColorScale={mutColorScale}
                dateRange={dateRange}
                width={width * dateGraphSpecs.w}
                height={height * dateGraphSpecs.h}
            ></DateGraph>
            <g transform={`translate(${width - 100}, 20)`}>
                <ColorLegend
                    mutColorScale={mutColorScale}
                ></ColorLegend>
            </g>
            <g transform={`translate(0, ${height * dateGraphSpecs.h})`}>
                <MutantMap
                    landscapeData={landscapeData}
                    laneLengths={laneLengths}
                    laneExist={laneExist}
                    mutColorScale={mutColorScale}
                    maxRatioSum={maxRatioSum}
                    width={width * landscapeSpecs.w}
                    height={height * landscapeSpecs.h}
                ></MutantMap>
            </g>
        </svg>
    );
};

createRoot(root).render(<App />);
