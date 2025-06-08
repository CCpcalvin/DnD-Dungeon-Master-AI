from django.contrib import admin

# Register your models here.
from .models import (
    GameSession,
    GameEvent,
    PlayerInfo,
    FloorHistoryModel,
    NonCombatFloorModel,
)

admin.site.register(GameSession)
admin.site.register(GameEvent)
admin.site.register(PlayerInfo)
admin.site.register(FloorHistoryModel)
admin.site.register(NonCombatFloorModel)
