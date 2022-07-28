import React, { useEffect, useState } from "react";
import { createRoot } from "react-dom/client";
import { scaleOrdinal, schemeSet1 } from "d3";
import { useData } from "./loadData";
import { MutantMap, DateGraph, ColorLegend } from "./components";

const root = document.getElementById("mutantLandscape");

const landscapeSpecs = { h: 0.8, w: 1 };
const dateGraphSpecs = { h: 1 - landscapeSpecs.h, w: 1 };

const App = () => {

    const [width, setWidth] = useState(root.offsetWidth);
    const [height, setHeight] = useState(root.offsetHeight);
    const [hoveredMut, setHoveredMut] = useState(null);
    const [selectedMuts, setSelectedMuts] = useState([]);
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

    const data = useData();
    if (!data) { return <pre>Loading...</pre>; };
    const [landscapeMap, mutDailyFreq, dateRange] = data;

    const mutColorScale = scaleOrdinal().domain(mutDailyFreq.keys()).range(schemeSet1);

    return (
        <svg width={width} height={height}>
            <g transform={`translate(0, ${height * dateGraphSpecs.h})`}>
                <MutantMap
                    landscapeMap={landscapeMap}
                    mutColorScale={mutColorScale}
                    width={width * landscapeSpecs.w}
                    height={height * landscapeSpecs.h}
                    hoveredMut={hoveredMut}
                    brushExtent={brushExtent}
                    selectedMuts={selectedMuts}
                ></MutantMap>
            </g>
            <DateGraph
                mutDailyFreq={mutDailyFreq}
                mutColorScale={mutColorScale}
                dateRange={dateRange}
                width={width * dateGraphSpecs.w}
                height={height * dateGraphSpecs.h}
                hoveredMut={hoveredMut}
                setBrushExtent={setBrushExtent}
                selectedMuts={selectedMuts}
            ></DateGraph>
            <g transform={`translate(${width - 100}, 20)`}>
                <ColorLegend
                    mutColorScale={mutColorScale}
                    hoveredMut={hoveredMut}
                    setHoveredMut={setHoveredMut}
                    selectedMuts={selectedMuts}
                    setSelectedMuts={setSelectedMuts}
                ></ColorLegend>
            </g>
        </svg>
    );
};

createRoot(root).render(<App />);
