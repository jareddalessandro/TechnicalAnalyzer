import technicals as TA
import numpy as np


############ INDICATOR Logic Functions ##############
# Each function will need to add points to either the buy or sell counter 
# Each function should take:
    # 'data' as an input, which will contain candle data in OHLCV format
    # buy_points as an input which will represent the growing quantity of buy indications seen
    # sell_points as an input will will represent the growing quantity of sell indications seen
    # weight, a modifier we can use to determine how crucial each specific usage of the function is

def analyze_rsi(data, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):
    rsi = TA.get_rsi(data)
    if (rsi > 68):
        analysis += '\nRSI becoming overbought'
        BEARISH_POINTS += (5 * weight)
    elif (rsi < 32):
        analysis += '\nRSI becoming oversold'
        BULLISH_POINTS += (5 * weight)
    return rsi, BULLISH_POINTS, BEARISH_POINTS, analysis


def analyze_ema_9(data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):
    ema = TA.get_ema_9(data)    
    return analyze_line(data, ema, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight)

# Returns line, BULLISH_POINTS, BEARISH_POINTS, analysis
def analyze_ema_50(data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):
    ema = TA.get_ema_50(data)
    return analyze_line(data, ema, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight)

# Returns line, BULLISH_POINTS, BEARISH_POINTS, analysis
def analyze_ema_120(data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):
    ema = TA.get_ema_120(data)
    return analyze_line(data, ema, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight)

# Returns line, BULLISH_POINTS, BEARISH_POINTS, analysis
def analyze_ema_200(data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):
    ema = TA.get_ema_200(data)
    return analyze_line(data, ema, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight)

# Returns line, BULLISH_POINTS, BEARISH_POINTS, analysis
def analyze_range_high(data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):
    range_high = get_range_high(data)
    return analyze_line(data, range_high, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight)

# Returns line, BULLISH_POINTS, BEARISH_POINTS, analysis
def analyze_range_low(data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):
    range_low = get_range_low(data)
    return analyze_line(data, range_low, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight)

# Analyze if we are close to one of the user defined prices
def analyze_user_defined_levels(levels, data, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight=1):

    for level in levels:        
        if (is_close_to_line(current_price, level)):
            # Approaching a line of resistence
            if (is_below_line(current_price, level) and is_short_term_going_up(current_price, data)):
                analysis += f"\nApproaching line of resistence - ${level}"
                BEARISH_POINTS += 5 * weight
            # Approaching a line of support
            elif (is_above_line(current_price, level) and is_short_term_going_down(current_price, data)):
                analysis += f'\nApproaching a line of support - ${level}'
                BULLISH_POINTS += 5 * weight
            # Broke through the line of resistence
            elif (is_above_line(current_price, level) and is_short_term_going_up(current_price, data)):
                analysis += f'\nApproaching a line of support - ${level}'
                BULLISH_POINTS += 10 * weight
            # Broke through the line of support
            elif (is_below_line(current_price, level) and is_short_term_going_down(current_price, data)):
                analysis += f'\nBroke through the line of support - ${level}'
                BEARISH_POINTS += 10 * weight

    return BULLISH_POINTS, BEARISH_POINTS, analysis



############ Direction Behavior Helper Functions ##############

def analyze_line(data, line, current_price, BULLISH_POINTS, BEARISH_POINTS, analysis, weight):    
    if (is_close_to_line(current_price, line)):
        # Approaching a line of resistence
        if (is_below_line(current_price, line) and is_short_term_going_up(current_price, data)):
            analysis += f"\nApproaching line of resistence - ${line}"
            BEARISH_POINTS += 5 * weight
        # Approaching a line of support
        elif (is_above_line(current_price, line) and is_short_term_going_down(current_price, data)):
            analysis += f'\nApproaching a line of support - ${line}'
            BULLISH_POINTS += 5 * weight
        # Broke through the line of resistence
        elif (is_above_line(current_price, line) and is_short_term_going_up(current_price, data)):
            analysis += f'\nApproaching a line of support - ${line}'
            BULLISH_POINTS += 10 * weight
        # Broke through the line of support
        elif (is_below_line(current_price, line) and is_short_term_going_down(current_price, data)):
            analysis += f'\nBroke through the line of support - ${line}'
            BEARISH_POINTS += 10 * weight
    return line, BULLISH_POINTS, BEARISH_POINTS, analysis


def is_above_line(current_price, line):
    if current_price > line:
        return True
    else:
        return False

def is_below_line(current_price, line):
    if current_price < line:
        return True
    else:
        return False

def is_close_to_line(current_price, line):
    sum = current_price - line
    if (sum <= .30 and sum >= -.30):
        return True
    else:
        return False

# Get the lowest value for the range provided
def get_range_low(data):
    lowest_low = data['open'][0]
    lows = []
    lows = data['low']
    for i in range(len(lows)):
        if lows[i] <= lowest_low:
            lowest_low = lows[i]
    return lowest_low

# Get the highest value for the range provided
def get_range_high(data):
    highest_high = data['open'][0]
    highs = []
    highs = data['high']
    for i in range(len(highs)):
        if highs[i] >= highest_high:
            highest_high = highs[i]
    return highest_high

# Check to see if current price is higher than last candle close
def is_short_term_going_up(current_price, data):
    length = len(data['close'])
    if current_price >= data['close'][length -1]:
        return True
    else:
        return False

# Check to see if current price is higher than last candle close
def is_short_term_going_down(current_price, data):
    length = len(data['close'])
    if current_price <= data['close'][length -1]:
        return True
    else:
        return False