import operator as op
from dataclasses import dataclass, field

operator_repr = {
    op.eq: "==",
    op.ne: "!=",
    op.ge: ">=",
    op.gt: ">",
    op.le: "<=",
    op.lt: "<",
}


@dataclass
class Recommendation:
    config: str
    formula: str
    operator: callable
    sources: list[str] = field(default_factory=list)

    def __str__(self):
        return f"{self.config} {operator_repr[self.operator]} {self.formula}"

    def evaluate(self, context: dict) -> str:
        rendered_formula = self.formula.format(**context)
        evaluated_formula = eval(rendered_formula)
        parts = [self.config, operator_repr[self.operator], evaluated_formula]
        if str(evaluated_formula) != str(self.formula):
            parts.append(f"({self.formula.replace('{', '').replace('}', '')})")
        return " ".join(map(str, parts))

    def render(self, context: dict) -> str:
        evaluation = self.evaluate(context)
        sources = "\n".join([f"* {source}" for source in self.sources])
        return f"{evaluation}\n{sources}"


recommendations = [
    Recommendation(
        config="num.io.threads",
        formula="{num_disks}",
        operator=op.eq,
        sources=["https://strimzi.io/blog/2021/06/08/broker-tuning/"],
    ),
    Recommendation(
        config="replica.fetch.min.bytes",
        formula="512",
        operator=op.eq,
        sources=[
            "https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/"
        ],
    ),
    Recommendation(
        config="socket.receive.buffer.bytes",
        formula="512",
        operator=op.eq,
        sources=[
            "https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/",
            "https://strimzi.io/blog/2021/06/08/broker-tuning/",
        ],
    ),
    Recommendation(
        config="socket.send.buffer.bytes",
        formula="1048576",
        operator=op.eq,
        sources=[
            "https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/",
            "https://strimzi.io/blog/2021/06/08/broker-tuning/",
        ],
    ),
    Recommendation(
        config="replica.socket.receive.buffer.bytes",
        formula="1048576",
        operator=op.eq,
        sources=[
            "https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/"
        ],
    ),
    Recommendation(
        config="socket.request.max.bytes",
        formula="104857600",
        operator=op.eq,
        sources=[
            "https://azure.microsoft.com/en-us/blog/processing-trillions-of-events-per-day-with-apache-kafka-on-azure/"
        ],
    ),
]
