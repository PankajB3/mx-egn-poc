module.exports = {
  apps : [{
    script: 'app.py',
    watch: '.'
  }, 
  // {
  //   script: './service-worker/',
  //   watch: ['./service-worker']
  // }
],

  deploy : {
    production : {
      user : 'SSH_USERNAME',
      host : 'SSH_HOSTMACHINE',
      ref  : 'origin/master',
      repo : 'GIT_REPOSITORY',
      path : 'DESTINATION_PATH',
      'pre-deploy-local': '',
      'post-deploy' : 'pip install -r requirements.txt && pm2 reload ecosystem.config.js --env production',
      'pre-setup': ''
    }
  }
};
