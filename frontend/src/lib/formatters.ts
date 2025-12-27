/**
 * Format utilities for consistent number display
 */

/**
 * Round a percentage to a whole number
 * @param value - The percentage value (0-100)
 * @returns Rounded percentage as integer
 */
export function roundPercent(value: number): number {
    return Math.round(value);
}

/**
 * Format a percentage for display with % symbol
 * @param value - The percentage value (0-100)
 * @param decimals - Number of decimal places (default: 0)
 * @returns Formatted percentage string with % symbol
 */
export function formatPercent(value: number, decimals: number = 0): string {
    return `${value.toFixed(decimals)}%`;
}

/**
 * Round a decimal to specified precision
 * @param value - The number to round
 * @param decimals - Number of decimal places (default: 1)
 * @returns Rounded number
 */
export function roundDecimal(value: number, decimals: number = 1): number {
    const factor = Math.pow(10, decimals);
    return Math.round(value * factor) / factor;
}

/**
 * Format a risk score (0-100) with consistent rounding
 * @param score - Risk score value
 * @returns Rounded integer risk score
 */
export function formatRiskScore(score: number): number {
    return Math.round(Math.max(0, Math.min(100, score)));
}

/**
 * Format confidence value (0-1 or 0-100) to percentage
 * @param confidence - Confidence value
 * @param isDecimal - If true, value is 0-1, if false 0-100
 * @returns Formatted percentage string
 */
export function formatConfidence(confidence: number, isDecimal: boolean = true): string {
    const pct = isDecimal ? confidence * 100 : confidence;
    return `${Math.round(pct)}%`;
}
