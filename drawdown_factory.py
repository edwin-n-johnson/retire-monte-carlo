from enum import Enum
from drawdown import Drawdown
from drawdown_const_percentage import DrawdownConstPercentage
# from drawdown_const_dollars import DrawdownConstDollars
# from drawdown_guardrails import DrawdownGuardrails
# from drawdown_mad_fientist import DrawdownMadFientist
from drawdown_buckets import DrawdownBuckets


class DrawdownTypes(Enum):
    CONST_PERCENT = 1
    CONST_DOLLARS = 2
    GUARD_RAILS = 3
    MAD_FIENTIST = 4
    BUCKETS = 5


def create_drawdown(drawdown: DrawdownTypes, *args, **kwargs) -> Drawdown:
    drawdown_obj = None

    if drawdown == DrawdownTypes.CONST_PERCENT:
        drawdown_obj = DrawdownConstPercentage(args, kwargs)
    elif drawdown == DrawdownTypes.CONST_DOLLARS:
        # drawdown_obj = DrawdownConstDollars(args, kwargs)
        pass
    elif drawdown == DrawdownTypes.GUARD_RAILS:
        # drawdown_obj = DrawdownGuardrails(args, kwargs)
        pass
    elif drawdown == DrawdownTypes.MAD_FIENTIST:
        # drawdown_obj = DrawdownMadFientist(args, kwargs)
        pass
    elif drawdown == DrawdownTypes.BUCKETS:
        drawdown_obj = DrawdownBuckets(args, kwargs)
    else:
        raise RuntimeError(f"Invalid drawdown option: {drawdown}")

    return drawdown_obj
