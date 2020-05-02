from dataclasses import dataclass

from ...models.tracking import DataSet as TrackingDataSet
from ...models.event import DataSet as EventDataSet
from ...models.common import DataSetFlag, Team, BallState


class TrackingPossessionEnricher:
    def enrich_inplace(self, tracking_data_set: TrackingDataSet, event_data_set: EventDataSet) -> None:
        """
            Return an enriched tracking data set.

            Use the event data to rebuild game state.

            Iterate through all tracking data events and apply event data to the GameState whenever
            they happen.

        """
        if tracking_data_set.flags & (DataSetFlag.BALL_OWNING_TEAM | DataSetFlag.BALL_STATE):
            return

        if not event_data_set.flags & (DataSetFlag.BALL_OWNING_TEAM | DataSetFlag.BALL_STATE):
            raise Exception("Event DataSet does not contain ball owning team or ball state information")

        # set some defaults
        next_event_idx = 0

        current_ball_owning_team = Team.HOME
        current_ball_state = BallState.DEAD

        for frame in tracking_data_set.records:
            if next_event_idx < len(event_data_set.records):
                event = event_data_set.records[next_event_idx]
                if frame.period == event.period and frame.timestamp >= event.timestamp:
                    current_ball_owning_team = event.ball_owning_team
                    current_ball_state = event.ball_state
                    next_event_idx += 1

            frame.ball_owning_team = current_ball_owning_team
            frame.ball_state = current_ball_state
