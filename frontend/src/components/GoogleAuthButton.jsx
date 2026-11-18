import { GoogleOAuthProvider, GoogleLogin } from "@react-oauth/google";

export default function GoogleAuthButton({ onCredential, onError, text = "Continue with Google" }) {
  const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID;
  const isConfigured =
    clientId && !clientId.includes("your-google-web-client-id");

  if (!isConfigured) {
    return (
      <div className="w-full mb-6">
        <button
          type="button"
          disabled
          className="w-full py-3 px-4 rounded-xl border border-slate-300 bg-slate-100 text-slate-400 font-bold text-sm shadow-sm cursor-not-allowed"
          title="Set a real VITE_GOOGLE_CLIENT_ID in the project .env file"
        >
          {text}
        </button>
        <p className="mt-2 text-center text-xs text-slate-500">
          Google sign-in needs a real OAuth client ID in the project .env file.
        </p>
      </div>
    );
  }

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <div className="w-full mb-6 [&>div]:w-full [&_iframe]:mx-auto">
        <GoogleLogin
          onSuccess={(credentialResponse) =>
            onCredential(credentialResponse.credential)
          }
          onError={onError}
          text={text === "Sign up with Google" ? "signup_with" : "signin_with"}
          width="400"
          shape="pill"
        />
      </div>
    </GoogleOAuthProvider>
  );
}
