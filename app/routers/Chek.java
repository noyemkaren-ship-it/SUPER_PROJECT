class Chek {
    public static void main(String[] args) {
        String password = args[0];
        int score = 0;

        if (password == null || password.isEmpty()) {
            System.out.println("empty");
            return;
        }

        if (password.length() < 8) {
            score -= 10;
        }
        if (password.matches(".*\\d.*")) {
            score += 10;
        }
        if (password.length() > 15) {
            score += 20;
        }
        if (password.length() > 8) {
            score += 10;
        }
        if (password == "123456") {
            score -= 100;
        }
        if (password.matches(".*[A-Z].*")) {
            score += 20;
        }

        if (score > 30) {
            System.out.println("strong");
            return;
            
        }
        if (score > 10) {
            System.out.println("medium");
            return;

        }
        if (score < 10) {
            System.out.println("weak");
            return;
        }
}}