# CI/CD Deployment Guide: World Tour

To complete the **World Class** deployment, follow these steps to set up your GitHub repository and connect it to Google Cloud and Firebase.

## 1. Google Cloud Setup (Project: `world-tour-474018`)

### Create a Service Account
1. Go to **IAM & Admin > Service Accounts** in the [Google Cloud Console](https://console.cloud.google.com/).
2. Click **Create Service Account**.
3. Name: `github-deployer`.
4. Grant the following roles:
   - **Cloud Run Admin**
   - **Artifact Registry Administrator**
   - **Storage Admin**
   - **Service Account User**
5. Create a **JSON Key** for this service account and download it.

## 2. Firebase Setup (Project: `world-tour-f6f23`)

### Get Firebase Service Account
1. Go to **Project Settings > Service accounts** in the [Firebase Console](https://console.firebase.google.com/).
2. Click **Generate new private key** and download the JSON.

## 3. GitHub Repository Secrets

Add the following secrets to your GitHub repository (**Settings > Secrets and variables > Actions**):

| Secret Name | Value |
|-------------|-------|
| `GCP_SA_KEY` | Paste the content of the Google Cloud JSON key. |
| `FIREBASE_SERVICE_ACCOUNT_WORLD_TOUR_F6F23` | Paste the content of the Firebase JSON key. |

## 4. Deploy!

Once you push your code to GitHub (branch `main` or `master`), the workflow will automatically:
1. Build the **Flask Backend** into a Docker container.
2. Deploy the container to **Google Cloud Run**.
3. Build the **React Frontend** using Vite + Tailwind 4.
4. Deploy the static assets to **Firebase Hosting**.
5. Unified URL: Your Firebase Hosting URL will serve the React app and proxy `/auth`, `/booking`, etc., to Cloud Run.
