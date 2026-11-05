# Popular News daily refresh

The workflow runs daily at 11:00 UTC (7:00 a.m. in Santo Domingo) and can also be run from Actions. It reads property `559369724` through the Google Analytics Data API and uses the GA4 property's own timezone for the 30 complete days. It commits the verified snapshot and deploys when the homepage cards change. A failed query or invalid ranking leaves the published ranking intact.

## Connect GitHub to Google Analytics

1. In a Google Cloud project, enable the Google Analytics Data API, IAM Credentials API and Security Token Service API. Create a dedicated service account for Popular News.
2. In Google Analytics, open Admin → Property access management for property `559369724` and add the service account email as a **Viewer**.
3. Configure a GitHub OIDC Workload Identity Federation provider. Restrict the provider to this repository and the main branch and grant only that identity `roles/iam.workloadIdentityUser` on the dedicated service account. Use numeric owner and repository IDs in the provider's conditions where possible.
4. In GitHub Settings → Secrets and variables → Actions → Variables, add `GA4_WIF_PROVIDER` (full provider resource name) and `GA4_SERVICE_ACCOUNT` (service account email). Neither value is a private key.
5. Run **Refresh Popular News from GA4** from the Actions tab on main. Check that it reports the date range, and verify that changed cards trigger the existing Deploy AniNextUp Worker workflow.

Until both variables are present the workflow skips the GA4 request and preserves the existing snapshot.

- [Google GitHub Actions authentication setup](https://github.com/google-github-actions/auth#setting-up-workload-identity-federation)
- [Analytics Data API setup](https://developers.google.com/analytics/devguides/reporting/data/v1/quickstart)
