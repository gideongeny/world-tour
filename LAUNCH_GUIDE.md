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
I have automated the push for you. All your latest features are now in your repository.

### Step B: Connect to Vercel
1. Log in to [vercel.com](https://vercel.com).
2. Click **Add New** > **Project**.
3. Import your `world-tour` repository.
4. **Environment Variables**: This is critical for your APIs to work.
   - Go to your Project **Settings** -> **Environment Variables**.
   - Add the following keys and values:
     - `LITEAPI_SANDBOX_KEY`: `sand_6e482b71-1bc4-4c45-b18c-cd0cd4977587`
     - `LITEAPI_PUBLIC_KEY`: `cfff8058-e454-4bff-abaf-8e6f0b44d6bb`
     - `HOTELBEDS_API_KEY`: `0f01a4e17c5508c923224a2ddf30c7d7`
     - `STRIPE_SECRET_KEY`: (Your Stripe Secret Key)
     - `STRIPE_PUBLISHABLE_KEY`: (Your Stripe Publishable Key)
     - `GOOGLE_API_KEY`: (Your Gemini key)
5. Click **Deploy**.

---

## 4. Initializing your Production Site
Once the deployment is green:
1. Visit your Vercel URL (e.g., `https://world-tour.vercel.app`).
2. Navigate to `your-url.vercel.app/seed` to initialize the database.
3. Your site is live! Your search bar will now use **LiteAPI** for live results and **Hotelbeds** as a powerful backup.

---

## 5. Summary Checklist
- [ ] `vercel.json` present in root.
- [ ] `GOOGLE_API_KEY` added in Vercel.
- [ ] Vercel Postgres storage connected.
- [ ] Code pushed to GitHub.
- [ ] Visited `/seed` to initialize data.

---
*Last deployment trigger: 2026-01-09*
