# BROWSER CLEANUP RULE (ALL CRONS)

**Every cron job that uses the browser MUST do this as its ABSOLUTE LAST step:**

1. List all open tabs (`browser tabs`)
2. Close any tabs that are NOT `http://localhost:3000` 
3. Navigate the remaining tab to `http://localhost:3000` if it isn't already
4. Focus the dashboard tab
5. Release browser lock if held

The desktop screen must ALWAYS show the Jane Dashboard when any cron job finishes.
Josh monitors this screen constantly. Leaving X analytics, Sorare, Gmail, or any other site visible is a bug.
