# SpotifyTrueDaily UI Update - TODO List

## Phase 1: Color Scheme Update
- [ ] Update ModernTheme class colors from Spotify green to dark blue/violet
- [ ] Update accent colors in all UI components
- [ ] Update button hover states and borders

## Phase 2: Navigation Restructure
- [ ] Simplify sidebar navigation to only "Playlist configuration" and "Settings"
- [ ] Remove Dashboard and About sections
- [ ] Update navigation handlers in app_modern.py

## Phase 3: New Playlist Configuration Tab
- [ ] Create new PlaylistConfiguration view class
- [ ] Add playlist info display (name, track count, last updated)
- [ ] Design configuration cards layout

## Phase 4: Configuration Cards Implementation
- [ ] Recent tracks configuration card (toggle + limit)
- [ ] Favorites/top tracks configuration card (toggle + limit)
- [ ] Podcast episodes configuration card (toggle + limit)
- [ ] Random recommendations configuration card (toggle + limit)
- [ ] SoundStat recommendations configuration card (toggle + limit)

## Phase 5: Parameter Integration
- [ ] Connect all configuration cards to config.py parameters
- [ ] Ensure real-time config updates
- [ ] Add validation for numeric inputs

## Phase 6: Testing & Polish
- [ ] Test "Refresh now" button functionality
- [ ] Verify all configuration changes persist
- [ ] Test UI responsiveness and layout
- [ ] Final visual polish and consistency check
