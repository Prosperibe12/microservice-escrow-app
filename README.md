### Escrow Trust

`Escrow Trust` is an escrow application designed to facilitate secure transactions between buyers and sellers. It acts as a reliable third party, ensuring that both parties fulfill their agreed-upon terms before completing a transaction. Escrow Trust provides a secure and trustworthy platform that facilitates online transactions. With the rise of online commerce, there is an increasing demand for a system that ensures the safety and transparency of transactions between unknown parties.

### Overview
Escrow Trust provides a seamless and secure environment for buyers and sellers to engage in transactions. Written in Python using the Django framework, it leverages Docker for easy deployment and scalability. The application incorporates features such as instant email and push notifications, an analytics-enriched dashboard, and robust user settings to enhance the overall user experience.

### Features
* `Secure Transaction Handling:` Escrow Trust acts as a mediator, holding the funds until both the buyer and seller meet their obligations. This ensures that both parties are protected throughout the transaction.

* `Real-time Notifications:` Users receive instant email and push notifications to stay informed about the status of their transactions. This feature enhances communication and keeps users updated on critical events.

* `Analytics-Enriched Dashboard:` The application provides a comprehensive dashboard with analytics tools, allowing users to track and analyze their transaction history. This feature empowers users with valuable insights into their buying and selling patterns.

* `User Settings:` Escrow Trust offers customizable user settings, allowing users to tailor their experience according to their preferences. From notification preferences to security settings, users have control over their account settings.

### Getting Started

To run Escrow Trust locally, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/Prosperibe12/microservice-escrow-app.git
    ```

2. Update Database credentials in `settings.py` file:

    ```bash
    cd escrow_app/project_core/settings.py and update database credentials with your local db credentials.
    ```
3. Navigate to the project directory:

    ```bash
    cd escrow_app
    ```
4. Build and run the Docker containers:

    ```bash
    docker-compose up
    ```

5. Access the application at [http://localhost:8000](http://localhost:8000) in your web browser.

For a production deployment, ensure that you have Docker and Docker Compose installed. Update the necessary environment variables in the Docker Compose file to match your production environment.

### Contributing

Contributions are welcome! If you'd like to contribute to Escrow Trust, please email [Prosperibe12@gmail.com](CONTRIBUTING.md).

### License

This project is licensed under the [MIT License](LICENSE).

