import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { group, scaleOrdinal, schemeSet1 } from "d3";
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
    const [hoveredMut, setHoveredMut] = useState(null);
    const [brushExtent, setBrushExtent] = useState(null);

    useEffect(() => {
        const handleResize = () => {
            setWidth(root.offsetWidth);
            setHeight(root.offsetHeight);
        };
        window.addEventListener("resize", handleResize);
        return () => {
            window.removeEventListener("resize", handleResize);
        };
    }, []);

    const data = LoadData();
    if (!data) { return <pre>Loading...</pre>; };
    const [
        landscapeData,
        dailyMutFreq,
        maxRatioSum,
        dateRange
    ] = data;

    const mutDailyFreq = group(dailyMutFreq, d => d["mut"]);
    const mutColorScale = scaleOrdinal().domain(mutDailyFreq.keys()).range(schemeSet1);

    return (
        <svg width={width} height={height}>
            <DateGraph
                mutDailyFreq={mutDailyFreq}
                mutColorScale={mutColorScale}
                dateRange={dateRange}
                width={width * dateGraphSpecs.w}
                height={height * dateGraphSpecs.h}
                hoveredMut={hoveredMut}
            ></DateGraph>
            <g transform={`translate(${width - 100}, 20)`}>
                <ColorLegend
                    mutColorScale={mutColorScale}
                    hoveredMut={hoveredMut}
                    setHoveredMut={setHoveredMut}
                ></ColorLegend>
            </g>
            <g transform={`translate(0, ${height * dateGraphSpecs.h})`}>
                <MutantMap
                    landscapeData={landscapeData}
                    mutColorScale={mutColorScale}
                    maxRatioSum={maxRatioSum}
                    width={width * landscapeSpecs.w}
                    height={height * landscapeSpecs.h}
                    hoveredMut={hoveredMut}
                ></MutantMap>
            </g>
        </svg>
    );
};

createRoot(root).render(<App />);
