# 🚀 Launch Guide: World Tour (Vercel Edition)

This guide explains how to launch your **World Tour** website as a single, fully functional site (Frontend + Backend) using GitHub and Vercel.

---

## 1. Project Configuration
I have already created a `vercel.json` in your root directory. This file tells Vercel:
- **Backend**: Use Python to serve the Flask app via `api/index.py`.
- **Frontend**: Build the React app in the `frontend` folder and serve the static files.

---

## 2. Setting Up the Database (Production)
> [!IMPORTANT]
> Vercel's serverless environment is **read-only**. You cannot use the `world_tour_v2.db` (SQLite) file successfully in production as it resets every time your server sleeps.

### Recommended: Vercel Postgres
1. Go to your project onto the **Vercel Dashboard**.
2. Click the **Storage** tab.
3. Select **Postgres** and click **Connect/Create**.
4. Once created, click **Connect to Project**.
5. Vercel will automatically add the environment variable `POSTGRES_URL`.

*The `app.py` code is already configured to automatically use `POSTGRES_URL` if it exists!*

---

## 3. Deployment Steps

### Step A: Push to GitHub
If you haven't pushed the latest `vercel.json` I just created:
```bash
git add vercel.json
git commit -m "Add Vercel deployment configuration"
git push origin main
```

### Step B: Connect to Vercel
1. Log in to [vercel.com](https://vercel.com).
2. Click **Add New** > **Project**.
3. Import your `world-tour` repository.
4. **Environment Variables**: Add your `GOOGLE_API_KEY` (from Gemini) to the project settings.
5. Click **Deploy**.

---

## 4. Initializing your Production Site
Once the deployment index is green:
1. Visit your Vercel URL (e.g., `https://world-tour.vercel.app`).
2. Navigate to `your-url.vercel.app/seed`. 
   - This will create the database tables in Postgres and populate them with your destinations and images.
3. Go back to your homepage — **Your site is live!** 🌍

---

## 5. Summary Checklist
- [ ] `vercel.json` present in root.
- [ ] `GOOGLE_API_KEY` added in Vercel.
- [ ] Vercel Postgres storage connected.
- [ ] Code pushed to GitHub.
- [ ] Visited `/seed` to initialize data.
