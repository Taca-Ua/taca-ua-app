from django.db.models import QuerySet
from ..models import Regulation


def render_regulations(regulations: QuerySet[Regulation]) -> QuerySet[Regulation]:
    return regulations

def render_regulation(regulation: QuerySet[Regulation] | Regulation) -> QuerySet[Regulation]:
    
    if isinstance(regulation, Regulation):
        regulation = Regulation.objects.filter(id=regulation.id)
    
    regulation = render_regulations(regulation)

    return regulation