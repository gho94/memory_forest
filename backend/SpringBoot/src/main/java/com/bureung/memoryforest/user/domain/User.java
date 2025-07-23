package com.bureung.memoryforest.user.domain;

import jakarta.persistence.*;
import lombok.*;

import java.util.Date;

@Entity
@Table(name = "users")
@Getter
@Setter
@NoArgsConstructor
@AllArgsConstructor
@Builder
public class User {
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    private String user_id;
    private String user_name;
    private String password;
    private String email;
    private String phone;
    private String user_type;
    private String file_id;
    private String status;
    private Date created_at;
    private Date updated_at;
    private Date deleted_at;
    private Date last_login_at;
}
