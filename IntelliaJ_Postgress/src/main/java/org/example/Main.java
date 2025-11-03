package org.example;

import java.sql.*;
import java.util.Scanner;

public class Main {

    // database connection info to login to Postgress
    private final String url = "jdbc:postgresql://localhost:5432/Assignment3";
    private final String user = "postgres";
    private final String password = "password";

    // display all students in database with all their variables
    public void getAllStudents() {
        //get all the details of the student structures (note secret primary key of student_id)
        String SQL = "SELECT * FROM students";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             Statement stmt = conn.createStatement();
             ResultSet res = stmt.executeQuery(SQL)) {

            System.out.println("\nAll Students:");
            //while future entries exist
            while (res.next()) {
                System.out.printf("ID: %d | Name: %s %s | Email: %s | Enrolled: %s%n",
                        res.getInt("student_id"),
                        res.getString("first_name"),
                        res.getString("last_name"),
                        res.getString("email"),
                        res.getDate("enrollment_date"));
            }
        //catch any issues
        } catch (SQLException ex) {
            System.out.println(ex.getMessage());//this gets the exit messgae given by postgre to intelliJ
        }
    }

    // add student funciton
    public void addStudent(String firstName, String lastName, String email, String enrollmentDate) {
        //follows declared structures that are part of the language of connection to postgre
        String SQL = "INSERT INTO students(first_name, last_name, email, enrollment_date) VALUES(?,?,?,?)";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             PreparedStatement pstmt = conn.prepareStatement(SQL)) {

            pstmt.setString(1, firstName);
            pstmt.setString(2, lastName);
            pstmt.setString(3, email);
            pstmt.setDate(4, Date.valueOf(enrollmentDate));
            pstmt.executeUpdate();
            System.out.println("Student added successfully!");

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    // update student function
    public void updateStudentEmail(int studentId, String newEmail) {
        String SQL = "UPDATE students SET email = ? WHERE student_id = ?";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             PreparedStatement pstmt = conn.prepareStatement(SQL)) {

            pstmt.setString(1, newEmail);
            pstmt.setInt(2, studentId);
            int rowsUpdated = pstmt.executeUpdate();

            if (rowsUpdated > 0)
                System.out.println("Student email updated successfully!");
            else
                System.out.println("Student not found!");

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    // delete student id funciton
    public void deleteStudent(int studentId) {
        String SQL = "DELETE FROM students WHERE student_id = ?";

        try (Connection conn = DriverManager.getConnection(url, user, password);
             PreparedStatement pstmt = conn.prepareStatement(SQL)) {

            pstmt.setInt(1, studentId);
            int rowsDeleted = pstmt.executeUpdate();

            if (rowsDeleted > 0)
                System.out.println("Student deleted successfully!");
            else
                System.out.println("Student not found!");

        } catch (SQLException ex) {
            System.out.println(ex.getMessage());
        }
    }

    //make a while loop for testing or such as well as just being the interface here
    public static void main(String[] args) {
        Main dbOps = new Main();
        Scanner scanner = new Scanner(System.in);

        while (true) {
            System.out.println("\nChoose an option:");
            System.out.println("1: View all students");
            System.out.println("2: Add a student");
            System.out.println("3: Update a student email");
            System.out.println("4: Delete a student");
            System.out.println("5: Exit");

            int choice = Integer.parseInt(scanner.nextLine());

            switch (choice) {
                case 1 -> dbOps.getAllStudents();
                case 2 -> {
                    System.out.print("First name: ");
                    String first = scanner.nextLine();
                    System.out.print("Last name: ");
                    String last = scanner.nextLine();
                    System.out.print("Email: ");
                    String email = scanner.nextLine();
                    System.out.print("Enrollment date (YYYY-MM-DD): ");
                    String date = scanner.nextLine();
                    dbOps.addStudent(first, last, email, date);
                }
                case 3 -> {
                    System.out.print("Student ID to update: ");
                    int id = Integer.parseInt(scanner.nextLine());
                    System.out.print("new email: ");
                    String newEmail = scanner.nextLine();
                    dbOps.updateStudentEmail(id, newEmail);
                }
                case 4 -> {
                    System.out.print("Student ID to delete: ");
                    int id = Integer.parseInt(scanner.nextLine());
                    dbOps.deleteStudent(id);
                }
                case 5 -> {
                    System.out.println("Program done");
                    scanner.close();
                    return;
                }
                default -> System.out.println("Invalid option");
            }
        }
    }
}
