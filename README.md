# Feature-selection-with-tables

### Experiment setup

#### Database Schema

- Artist  
  {artist: str, monthly_listeners: int}
- Music  
  {songs: str, artist: str, stream_counts: int}
- User  
  {user: str, fav_artist: str, hours_in_app: int}

#### Correlations

- Strong positive linear correlation between stream_counts and monthly_listeners.
- No correlation between hours_in_app and monthly_listeners.

#### Distributions

-
