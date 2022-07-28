export function mutationName(protein, pos, state) {
    return `${protein}_${pos}${state}`;
}

export function setMutOpacity(
    hoveredMut,
    mutName,
    selectedMuts,
    unhoveredOpacity,
    hoveredOpacity
) {
    unhoveredOpacity = unhoveredOpacity ?? 0.15;
    hoveredOpacity = hoveredOpacity ?? 1;

    if (hoveredMut) {
        if (selectedMuts.length === 0 || selectedMuts.includes(hoveredMut)) {
            return mutName === hoveredMut ?
                hoveredOpacity :
                unhoveredOpacity;
        };
        return mutName === hoveredMut || selectedMuts.includes(mutName) ?
            hoveredOpacity :
            unhoveredOpacity;
    } else if (selectedMuts.length === 0 || selectedMuts.includes(mutName)) {
        return hoveredOpacity;
    };
    return unhoveredOpacity;
}
