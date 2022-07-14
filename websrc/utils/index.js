export function mutationName(protein, pos, state) {
    return `${protein}_${pos}${state}`;
}

export function setMutOpacity(
    hoveredMut,
    mutName,
    unhoveredOpacity = 0.15,
    hoveredOpacity = 1
) {
    return hoveredMut && (mutName !== hoveredMut) ? unhoveredOpacity : hoveredOpacity;
}
