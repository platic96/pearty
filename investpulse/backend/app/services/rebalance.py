"""포트폴리오 리밸런싱 계산 서비스.

개인 전략 템플릿의 목표 자산배분과 현재 포트폴리오를 비교하여
리밸런싱 제안을 생성합니다.
"""

from app.schemas.portfolio import (
    RebalanceItem,
    RebalanceSuggestion,
    TargetAllocationResponse,
)

# 개인 전략 템플릿 기본 목표 배분 (03-personal-strategy-template.md 참조)
DEFAULT_TARGET_ALLOCATIONS = [
    {"category": "stocks", "sub_category": "us_growth_tech", "label": "미국 성장주/기술주", "target_pct": 15.0},
    {"category": "stocks", "sub_category": "us_large_etf", "label": "미국 대형주 (ETF)", "target_pct": 10.0},
    {"category": "stocks", "sub_category": "domestic_growth", "label": "국내 성장주", "target_pct": 8.0},
    {"category": "stocks", "sub_category": "emerging_markets", "label": "해외 ETF (신흥국)", "target_pct": 4.0},
    {"category": "stocks", "sub_category": "domestic_dividend", "label": "국내 배당/우량주", "target_pct": 3.0},
    {"category": "crypto", "sub_category": "btc", "label": "비트코인 (BTC)", "target_pct": 18.0},
    {"category": "crypto", "sub_category": "eth", "label": "이더리움 (ETH)", "target_pct": 10.0},
    {"category": "crypto", "sub_category": "altcoins", "label": "기타 알트코인", "target_pct": 7.0},
    {"category": "cash_bonds", "sub_category": "cash_bonds", "label": "현금/채권", "target_pct": 25.0},
]


class RebalanceService:
    """리밸런싱 계산기."""

    def calculate(
        self,
        targets: list[TargetAllocationResponse] | list[dict],
        current_values: dict[str, float],
        total_portfolio_value: float,
        threshold_pct: float = 5.0,
    ) -> RebalanceSuggestion:
        """현재 포트폴리오와 목표 배분을 비교하여 리밸런싱 제안 생성.

        Args:
            targets: 목표 배분 리스트 (category, sub_category, label, target_pct)
            current_values: {sub_category: 현재 가치(원)} 딕셔너리
            total_portfolio_value: 전체 포트폴리오 가치 합계
            threshold_pct: 리밸런싱 트리거 기준 (목표 대비 차이 %)

        Returns:
            RebalanceSuggestion: 리밸런싱 제안
        """
        items: list[RebalanceItem] = []
        needs_rebalance = False

        for target in targets:
            if isinstance(target, dict):
                cat = target["category"]
                sub_cat = target.get("sub_category", "")
                label = target.get("label", "")
                target_pct = target["target_pct"]
            else:
                cat = target.category
                sub_cat = target.sub_category
                label = target.label
                target_pct = target.target_pct

            current_value = current_values.get(sub_cat, 0.0)
            current_pct = (current_value / total_portfolio_value * 100) if total_portfolio_value > 0 else 0.0
            diff_pct = round(current_pct - target_pct, 2)
            target_value = total_portfolio_value * target_pct / 100

            if abs(diff_pct) >= threshold_pct:
                needs_rebalance = True

            adjust_amount = round(target_value - current_value)

            if adjust_amount > 0:
                action = "매수 필요"
            elif adjust_amount < 0:
                action = "매도 필요"
            else:
                action = "유지"

            items.append(
                RebalanceItem(
                    category=cat,
                    sub_category=sub_cat,
                    label=label,
                    target_pct=target_pct,
                    current_pct=round(current_pct, 2),
                    diff_pct=diff_pct,
                    current_value=round(current_value),
                    target_value=round(target_value),
                    action=action,
                    adjust_amount=adjust_amount,
                )
            )

        # 요약 문구 생성
        over_items = [i for i in items if i.diff_pct >= threshold_pct]
        under_items = [i for i in items if i.diff_pct <= -threshold_pct]

        summary_parts = []
        if needs_rebalance:
            summary_parts.append(f"리밸런싱이 필요합니다 (기준: ±{threshold_pct}%).")
            if over_items:
                labels = ", ".join(i.label for i in over_items)
                summary_parts.append(f"초과 배분: {labels}")
            if under_items:
                labels = ", ".join(i.label for i in under_items)
                summary_parts.append(f"부족 배분: {labels}")
        else:
            summary_parts.append(f"현재 포트폴리오가 목표 배분 범위 내에 있습니다 (기준: ±{threshold_pct}%).")

        return RebalanceSuggestion(
            total_portfolio_value=round(total_portfolio_value),
            rebalance_threshold_pct=threshold_pct,
            needs_rebalance=needs_rebalance,
            items=items,
            summary=" ".join(summary_parts),
        )
