# LinkedIn Post Draft

I spent a big part of my career in C++ and desktop software, including technical leadership work around planning, requirements, stakeholder alignment, and architectural decision-making.

While I was focused on that world, the mainstream application stack kept evolving. Cloud-native delivery, containers, infrastructure as code, and now AI-oriented tooling have become part of the baseline technical vocabulary, even for engineering leadership roles.

So I decided to refresh my hands-on understanding in a practical way: by building and deploying a very small backend service end to end.

I started with a minimal FastAPI application, containerized it with Docker, added CI checks for linting, tests, and image builds, and set up GitHub Actions to publish versioned container images to Amazon ECR using GitHub OIDC instead of long-lived AWS keys.

The next step is deploying it on AWS using ECS on Fargate behind an Application Load Balancer, with infrastructure defined in CDK.

I chose that path deliberately.

I could have used a simpler platform, but I wanted to understand the actual moving parts that come up in production environments:

- how CI and release pipelines connect to artifact publishing
- how IAM roles differ across GitHub Actions, ECS task execution, and application runtime
- how networking, subnets, security groups, and load balancers shape reachability
- how health checks and observability fit into a running service

I am not pretending this small project gave me deep production cloud experience. 
For me, it's value is in:

- rebuilding hands-on fluency with the modern stack
- understanding the operational and architectural mechanics directly
- becoming more credible in technical conversations about cloud-native systems
- connecting leadership experience with current implementation patterns

One thing I appreciate about doing this in a small, explicit project is that it keeps the system easy to reason about. When the service is tiny, the infrastructure and delivery choices are easier to inspect, question, and explain.

That has made the learning much more useful than passively reading about the services.

If you have made a similar transition, from desktop or traditional application development into cloud-native systems, I would be interested in what you found most valuable to build or study along the way.
