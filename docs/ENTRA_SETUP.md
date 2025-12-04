# Microsoft Entra External ID Setup Guide

To enable "Create Account" and "Google Login", you must configure **User Flows** and **Identity Providers** in the Microsoft Entra Admin Center. This cannot be done via code alone.

## 1. Enable Sign-up (Create Account)

1.  Sign in to the [Microsoft Entra Admin Center](https://entra.microsoft.com) and switch to your **External (CIAM)** tenant (`cc8dfa60...`).
2.  Navigate to **External Identities** > **User flows**.
3.  Click **+ New user flow**.
4.  **Name**: `UserFlow-1` (or similar).
5.  **Identity providers**: Select **Email with password** (and **Google** if you configured it, see below).
6.  **User attributes**: Select attributes to collect during sign-up (e.g., Display Name, Country/Region).
7.  Click **Create**.
8.  **Important**: Click on the newly created User Flow (`UserFlow-1`).
9.  Go to **Applications** > **Add application**.
10. Select **SecAI Radar** and click **Select**.

*This links the sign-up experience to your app. Without this, users only see "Sign In".*

## 2. Enable Google Login

1.  Go to [Google Cloud Console](https://console.cloud.google.com).
2.  Create a new Project (or use existing).
3.  **APIs & Services** > **OAuth consent screen** > **External** > Create.
    *   Fill in App Name, Support Email.
    *   **Authorized domains**: `ciamlogin.com` and `secairadar.cloud`.
4.  **Credentials** > **Create Credentials** > **OAuth client ID**.
    *   **Application type**: Web application.
    *   **Authorized redirect URIs**:
        *   `https://secairadar.ciamlogin.com/cc8dfa60-ec68-406a-bebf-63fcf331d433/federation/oidc/google`
5.  Copy the **Client ID** and **Client Secret**.

### Back in Microsoft Entra Admin Center:

1.  Navigate to **External Identities** > **Identity providers**.
2.  Click **+ Google**.
3.  Paste the **Client ID** and **Client Secret**.
4.  Click **Save**.
5.  **Add to User Flow**:
    *   Go back to **User flows** > `UserFlow-1`.
    *   **Identity providers**.
    *   Check **Google**.
    *   Click **Save**.

## 3. Enable Passkeys (FIDO2)

1.  Navigate to **Protection** > **Authentication methods**.
2.  Click **FIDO2 security key**.
3.  **Enable**: Yes.
4.  **Target**: All users.
5.  **Key restriction**: Allow all (or restrict as needed).
6.  Click **Save**.

*Note: Passkeys in CIAM are currently supported as a "Sign-in" method. Users typically register them after their first sign-in via `mysignins.microsoft.com`.*

## Troubleshooting

### Google Error: "401 invalid_client" / "The OAuth client was not found"
This means the **Client ID** you pasted into Entra does not match the one in Google Cloud Console.

1.  Go to [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials).
2.  Check the **Client ID** for your Web Application.
    *   It should look like: `123456789-abcde...apps.googleusercontent.com`.
    *   Make sure there are no extra spaces.
3.  Go to [Entra Admin Center > External Identities > Identity providers > Google](https://entra.microsoft.com/#view/Microsoft_AAD_IAM/CompanyRelationshipsMenuBlade/~/IdentityProviders).
4.  Re-paste the **Client ID** and **Client Secret**.
5.  Save.

### Google Error: "400 redirect_uri_mismatch"
This means the **Authorized redirect URI** in Google Cloud Console is missing or incorrect.

1.  Go to [Google Cloud Console > Credentials](https://console.cloud.google.com/apis/credentials).
2.  Click the pencil icon to edit your OAuth 2.0 Client ID.
3.  Under **Authorized redirect URIs**, ensure this **EXACT** URL is present (matches the one in your error message):
    ```
    https://secairadar.ciamlogin.com/cc8dfa60-ec68-406a-bebf-63fcf331d433/federation/oauth2
    ```
    *(Also keep the `/federation/oidc/google` one just in case, but the error specifically asked for `/federation/oauth2`)*.
4.  Click **Save**.
5.  Wait a few minutes (Google updates can take a moment) and try again.

## Branding & "ciamlogin.com"

If the Google screen says **"to continue to ciamlogin.com"**:
*   This is because your authentication URL is `https://secairadar.ciamlogin.com`.
*   To change this to `auth.secairadar.cloud`, you must configure a **Custom Domain** in the Entra Admin Center (requires DNS verification).

If the Google screen says **"Sign in to [Generic Name]"**:
*   Go to [Google Cloud Console > OAuth consent screen](https://console.cloud.google.com/apis/credentials/consent).
*   Edit the **App name** to "SecAI Radar".
*   Save.
