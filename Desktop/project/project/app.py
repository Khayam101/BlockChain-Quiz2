from hashlib import sha256
from secrets import token_hex

from flask import Flask, redirect, render_template, request, url_for


app = Flask(__name__)
app.secret_key = token_hex(32)

commitment_pool = []
nullifiers = []
transactions = []


def hash_pair(secret, nonce):
    return sha256(f"{secret}:{nonce}".encode("utf-8")).hexdigest()


def hash_value(value):
    return sha256(value.encode("utf-8")).hexdigest()


def merkle_root():
    if not commitment_pool:
        return hash_value("empty")

    level = commitment_pool[:]
    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        level = [
            hash_value(level[index] + level[index + 1])
            for index in range(0, len(level), 2)
        ]

    return level[0]


def new_private_value():
    return token_hex(16)


def mask_secret(secret):
    if len(secret) <= 12:
        return f"{secret[:3]}...{secret[-3:]}"
    return f"{secret[:6]}...{secret[-6:]}"


def public_transactions():
    return [transaction for transaction in transactions if transaction.get("public")]


@app.route("/mixer", methods=["GET", "POST"])
def mixer():
    deposit_data = None
    withdraw_result = None

    if request.method == "POST":
        action = request.form.get("action")

        if action == "deposit":
            secret = new_private_value()
            nonce = new_private_value()
            commitment = hash_pair(secret, nonce)

            commitment_pool.append(commitment)
            merkle_root()

            deposit_data = {
                "secret": secret,
                "masked_secret": mask_secret(secret),
                "nonce": nonce,
                "commitment": commitment,
            }

        if action == "withdraw":
            secret = request.form.get("secret", "").strip()
            nonce = request.form.get("nonce", "").strip()
            commitment = hash_pair(secret, nonce)
            nullifier = hash_value(secret)

            if not secret or not nonce:
                withdraw_result = {
                    "status": "error",
                    "title": "Invalid Proof",
                    "message": "Both fields are required.",
                }
            elif commitment not in commitment_pool:
                withdraw_result = {
                    "status": "error",
                    "title": "Invalid Proof",
                    "message": "The submitted credentials could not be verified.",
                }
            elif nullifier in nullifiers:
                withdraw_result = {
                    "status": "error",
                    "title": "Invalid Proof",
                    "message": "This withdrawal has already been used.",
                }
            else:
                commitment_pool.remove(commitment)
                nullifiers.append(nullifier)
                merkle_root()

                withdraw_result = {
                    "status": "success",
                    "title": "Withdrawal Successful",
                    "message": "The withdrawal request has been approved.",
                }

    return render_template(
        "mixer.html",
        deposit_data=deposit_data,
        withdraw_result=withdraw_result,
    )


@app.route("/")
def home():
    return redirect(url_for("mixer"))


@app.route("/transactions")
def transaction_log():
    return render_template(
        "transactions.html",
        public_transactions=public_transactions(),
    )


if __name__ == "__main__":
    app.run(port=5001)
