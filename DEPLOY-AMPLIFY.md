# Deploying the Inference ASIC Atlas to AWS Amplify Hosting

The site is static: 16 HTML pages and an `assets/` folder (CSS, JavaScript, fonts) in `site/dist/`.
There is no server code, and nothing has to be built on Amplify: the built site is committed.

Checked against the AWS documentation on 2026-10-12: the console steps of options A and B, the zip
layout, the precedence of `amplify.yml`, the 404 rule, the access-control path, and the options of
`create-branch`, `create-deployment` and `start-deployment`. Nothing here was run against an AWS
account from the environment that wrote it. The upload header in the `curl` line of option C is the
usual one but was not confirmed in the documentation.

## Option A: connect this repository (each push to `main` redeploys)

1. Open the Amplify console. Choose **Deploy an app** (first app in the Region) or **Create new app**.
2. On **Start building with Amplify**, choose **GitHub**, then **Next**. Amplify asks to install its
   GitHub App; give it access to `asic-calculator`.
3. On **Add repository branch**, select `yunistsao-maker/asic-calculator` and the branch `main`, then **Next**.
4. On **App settings**, the build settings come from `amplify.yml` in the repository root, which takes
   precedence over the console settings. It serves `site/dist` as it is:

   ```yaml
   version: 1
   frontend:
     phases:
       build:
         commands:
           - echo "site/dist is committed prebuilt; nothing to build"
     artifacts:
       baseDirectory: site/dist
       files:
         - '**/*'
   ```

   Create or pick a service role when asked, then **Next**.
5. On **Review**, choose **Save and deploy**. The site is served at `https://main.<app-id>.amplifyapp.com`.

## Option B: upload a zip (no Git connection)

1. Build the zip: `site/make.sh zip` writes `release/inference-asic-atlas-site.zip` with `index.html`
   at its root. To zip by hand, zip the *contents* of `site/dist`, not the folder: a zip with a
   top-level folder deploys but returns "Access Denied".
2. Amplify console: **Create new app** → **Deploy without Git** → **Next**.
3. Enter an app name and a branch name. For **Method**, choose **Drag and drop**, drop the zip, and
   choose **Save and deploy**.

## Option C: AWS CLI with the zip

```sh
APP_ID=$(aws amplify create-app --name inference-asic-atlas --query app.appId --output text)
aws amplify create-branch --app-id "$APP_ID" --branch-name main

# returns a job id and a pre-signed upload URL
aws amplify create-deployment --app-id "$APP_ID" --branch-name main \
  --query '[jobId,zipUploadUrl]' --output text
# paste the two values:
JOB_ID=...
UPLOAD_URL='...'

curl -H "Content-Type: application/zip" --upload-file release/inference-asic-atlas-site.zip "$UPLOAD_URL"
aws amplify start-deployment --app-id "$APP_ID" --branch-name main --job-id "$JOB_ID"
```

`start-deployment` has to follow `create-deployment` within 8 hours.

## Recommended for every option: the site's own "not found" page

`site/dist/404.html` exists, but Amplify serves it only with a rewrite rule. In the app, go to
**Hosting > Rewrites and redirects** and add this rule (the console's JSON editor accepts the content
of `amplify-redirects.json`):

```json
[
  { "source": "/<*>", "target": "/404.html", "status": "404", "condition": null }
]
```

## Optional settings

- **Private site.** Amplify Hosting can put a user name and password in front of a branch:
  Hosting > Access control > Manage access, then "Restricted-password required" for the branch.
  The site itself has no login.
- **Custom domain.** Hosting > Custom domains. All links in the site are relative, so the files need no
  change.
- **Search engines.** The pages carry no `noindex` tag. Add access control, or ask for a `noindex`
  build, if the site should stay out of search results.

## Updating the site

The content lives in `chapters/*.md`. After editing:

```sh
pip install -r site/requirements.txt     # markdown-it-py, beautifulsoup4
site/make.sh                             # rebuilds site/dist and runs the checks
git add -A && git commit -m "Update chapters" && git push
```

With option A the push redeploys. With options B and C, upload a new zip (`site/make.sh zip`).
Node.js is needed only for the model test and when a chapter gains a new formula (see `README.md`).

## What the site loads from outside

One stylesheet from Google Fonts (Noto Sans TC, for Traditional Chinese). If that request is blocked the
pages fall back to the system fonts (PingFang TC, Microsoft JhengHei). Everything else, including IBM Plex
and the KaTeX fonts, is in `site/dist/assets/`. Source links in the chapters open the original pages in a
new tab.
