# Widget Testing Checklist

## Local Testing (test.html)

### Setup
- [ ] `npm install` completed successfully
- [ ] `npm run build` created `dist/component.js`
- [ ] Open `test.html` in browser (or via `python3 -m http.server 8080`)

### Visual Tests
- [ ] Properties display in grid layout
- [ ] Images load (or show placeholder)
- [ ] Price displays correctly (£81,995 format)
- [ ] Bedrooms/bathrooms show with icons
- [ ] Postcode displays
- [ ] Garden badge shows (green)
- [ ] Parking badge shows (green)
- [ ] Status badge displays

### Interaction Tests
- [ ] Click property card → console logs "openExternal"
- [ ] Click favorite (🤍) → turns to ❤️
- [ ] Click favorite again → turns back to 🤍
- [ ] Console shows "setWidgetState" calls
- [ ] Sort dropdown changes property order
- [ ] Favorites count updates at top

### Theme Tests
- [ ] Click "Toggle Theme" button
- [ ] Background changes (white ↔ dark gray)
- [ ] Text color changes (dark ↔ light)
- [ ] Cards update colors
- [ ] Badges update colors

### Data Tests
- [ ] Click "Load Sample Data" → 3 properties appear
- [ ] Click "Clear Data" → "Loading properties..." shows
- [ ] Click "Load Sample Data" again → properties reappear

### Responsive Tests
- [ ] Resize browser to mobile width (< 640px)
- [ ] Grid becomes single column
- [ ] Cards remain readable
- [ ] Buttons still clickable

## Python Server Tests

### Unit Tests
```bash
python3 -m pytest test_server.py -v
```
- [ ] All 13 tests pass
- [ ] No errors or warnings

### Manual Server Test
```bash
python3 server.py --http
```
- [ ] Server starts on port 8000
- [ ] No errors in console
- [ ] Visit http://localhost:8000/health
- [ ] Returns `{"status": "healthy"}`

## ChatGPT Integration Tests

### Setup
- [ ] Server running with `--http`
- [ ] ngrok tunnel active
- [ ] ChatGPT connector configured
- [ ] Developer Mode enabled in chat

### Basic Tests
- [ ] Ask: "Show me properties in DY4"
- [ ] Widget loads inline
- [ ] Properties display correctly
- [ ] Images load

### Interaction Tests
- [ ] Click favorite button
- [ ] Refresh page → favorites persist
- [ ] Change sort order
- [ ] Click property → opens in new tab

### Filter Tests
- [ ] Ask: "Properties under £100k"
- [ ] Filter badge shows "💰 Under £100,000"
- [ ] All properties meet criteria

- [ ] Ask: "2 bedroom properties with parking"
- [ ] Filter badges show correctly
- [ ] Results match filters

### Theme Tests
- [ ] Switch ChatGPT to dark mode
- [ ] Widget updates automatically
- [ ] Colors look correct

### Error Tests
- [ ] Ask: "Properties in INVALID"
- [ ] Empty state shows
- [ ] Message: "No properties found"

## Performance Tests

### Bundle Size
```bash
ls -lh web/dist/component.js
```
- [ ] Size < 200KB
- [ ] Current: ~146KB ✅

### Build Time
```bash
cd web && time npm run build
```
- [ ] Build completes < 1 second
- [ ] Current: ~35ms ✅

### Load Time
- [ ] Widget appears < 1 second
- [ ] Images lazy load
- [ ] No layout shift

## Browser Compatibility

### Desktop
- [ ] Chrome/Edge (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)

### Mobile
- [ ] iOS Safari
- [ ] Android Chrome
- [ ] Responsive layout works

## Console Checks

### No Errors
- [ ] No red errors in console
- [ ] No React warnings
- [ ] No TypeScript errors

### Expected Logs
- [ ] "Sample data loaded" (test.html)
- [ ] "setWidgetState: ..." (when favoriting)
- [ ] "openExternal: ..." (when clicking card)

## Accessibility

### Keyboard Navigation
- [ ] Tab through cards
- [ ] Enter opens property
- [ ] Space toggles favorite

### Screen Reader
- [ ] Images have alt text
- [ ] Buttons have labels
- [ ] Semantic HTML used

## Edge Cases

### Empty State
- [ ] No properties → shows empty state
- [ ] Clear message displayed
- [ ] No errors

### Missing Data
- [ ] Missing image → placeholder shows
- [ ] Missing price → handles gracefully
- [ ] Missing postcode → handles gracefully

### Large Dataset
- [ ] 50+ properties → grid still works
- [ ] Scroll performance good
- [ ] No memory leaks

## Deployment Checklist

### Pre-Deploy
- [ ] All tests passing
- [ ] Bundle built and minified
- [ ] No console errors
- [ ] Documentation updated

### Deploy
- [ ] Server started with `--http`
- [ ] ngrok tunnel active
- [ ] ChatGPT connector updated
- [ ] Test in ChatGPT

### Post-Deploy
- [ ] Widget loads in ChatGPT
- [ ] All features work
- [ ] No errors in browser console
- [ ] No errors in server logs

## Known Issues

### Current Limitations
- No "Load More" button (planned for v2)
- No inline filter controls (planned for v2)
- No map view (planned for v3)

### Workarounds
- Use chat to refine filters
- Ask for more results: "Show me 10 properties"

## Success Criteria

### Must Pass
- ✅ All pytest tests pass
- ✅ Widget loads in test.html
- ✅ Widget loads in ChatGPT
- ✅ Favorites persist
- ✅ Sort works
- ✅ Dark mode works
- ✅ No console errors

### Should Pass
- ⭐ Images load quickly
- ⭐ Responsive on mobile
- ⭐ Smooth animations
- ⭐ Accessible via keyboard

## Troubleshooting

### Widget Not Loading
1. Check `dist/component.js` exists
2. Check browser console for errors
3. Verify ngrok URL is correct
4. Try test.html first

### Images Not Showing
1. Check network tab for 404s
2. Verify image URLs are valid
3. Check CORS headers
4. Fallback should show

### Favorites Not Persisting
1. Check console for setWidgetState calls
2. Verify window.openai is available
3. Check widget state in console
4. Try in test.html first

### Dark Mode Not Working
1. Check theme value in console
2. Verify data-theme attribute
3. Check CSS variables
4. Toggle theme in test.html

## Next Steps After Testing

1. ✅ All tests pass → Deploy to production
2. ⚠️ Some tests fail → Debug and fix
3. 📝 Document any issues
4. 🚀 Plan v2 features
