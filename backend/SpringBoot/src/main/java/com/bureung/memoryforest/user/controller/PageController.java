package com.bureung.memoryforest.user.controller;

import org.springframework.security.access.prepost.PreAuthorize;
import org.springframework.stereotype.Controller;
import org.springframework.web.bind.annotation.GetMapping;

@Controller
public class PageController {

    @GetMapping("/recorder")
    @PreAuthorize("hasAuthority('ROLE_A20001')")
    public String recorderPage() {
        return "forward:/";
    }

    @GetMapping("/companion")
    @PreAuthorize("hasAuthority('ROLE_A20002')")
    public String companionPage() {
        return "forward:/";
    }
}
