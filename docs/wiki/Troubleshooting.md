---
layout: default
title: Troubleshooting
permalink: /Troubleshooting/
---

# Troubleshooting Guide

Common issues and solutions for SecAI Radar.

---

## General Issues

### Application Not Loading

**Symptoms**:
- Blank page
- Error messages
- Page not found

**Solutions**:
1. **Check Browser**: Use modern browser (Chrome, Firefox, Safari, Edge)
2. **Clear Cache**: Clear browser cache and cookies
3. **Check URL**: Verify correct URL
4. **Check Network**: Verify network connection
5. **Check Console**: Check browser console for errors

---

## API Issues

### API Not Responding

**Symptoms**:
- API calls failing
- Timeout errors
- Connection errors

**Solutions**:
1. **Check API Status**: Verify API is running
2. **Check URL**: Verify API base URL
3. **Check Authentication**: Verify authentication is configured
4. **Check CORS**: Verify CORS settings
5. **Check Logs**: Check API logs for errors

### API Authentication Errors

**Symptoms**:
- 401 Unauthorized errors
- Authentication failures
- Token errors

**Solutions**:
1. **Check Credentials**: Verify API keys/secrets
2. **Check Expiration**: Verify tokens not expired
3. **Check Permissions**: Verify user has permissions
4. **Check Configuration**: Verify authentication configuration
5. **Check Azure AD**: Verify Azure AD settings

---

## Data Issues

### Controls Not Showing

**Symptoms**:
- Controls list empty
- Filters not working
- No data displayed

**Solutions**:
1. **Check Import**: Verify controls were imported
2. **Check Filters**: Clear filters to see all controls
3. **Check Tenant**: Verify correct tenant ID
4. **Check Storage**: Verify storage connection
5. **Check Data**: Verify data exists in storage

### Data Not Updating

**Symptoms**:
- Changes not reflected
- Stale data
- Old values showing

**Solutions**:
1. **Refresh Page**: Refresh browser page
2. **Clear Cache**: Clear browser cache
3. **Check Storage**: Verify storage updates
4. **Check API**: Verify API updates
5. **Check Timing**: Wait a few moments for processing

---

## Model Issues

### AI Models Not Working

**Symptoms**:
- AI analysis not working
- Model errors
- Timeout errors

**Solutions**:
1. **Check Configuration**: Verify `config/models.yaml`
2. **Check Azure OpenAI**: Verify Azure OpenAI access
3. **Check Deployment**: Verify model deployment exists
4. **Check API Keys**: Verify API keys are correct
5. **Check Quotas**: Verify quotas not exceeded

### Model Connection Errors

**Symptoms**:
- Connection errors
- Authentication failures
- Endpoint errors

**Solutions**:
1. **Check Endpoint**: Verify endpoint URL
2. **Check Authentication**: Verify authentication method
3. **Check Network**: Verify network connectivity
4. **Check Firewall**: Verify firewall rules
5. **Check Logs**: Check model provider logs

---

## UI Issues

### Dashboard Not Loading

**Symptoms**:
- Dashboard blank
- Metrics not showing
- Charts not rendering

**Solutions**:
1. **Check Data**: Verify data exists
2. **Check API**: Verify API is responding
3. **Check Filters**: Clear filters
4. **Check Browser**: Use modern browser
5. **Check Console**: Check browser console

### Controls Not Displaying

**Symptoms**:
- Controls table empty
- Import not working
- Filters not working

**Solutions**:
1. **Check Import**: Verify CSV import succeeded
2. **Check Format**: Verify CSV format
3. **Check Filters**: Clear filters
4. **Check Tenant**: Verify correct tenant
5. **Check Storage**: Verify storage connection

### Tools Not Saving

**Symptoms**:
- Tool configuration not saving
- Error messages
- Changes not persisting

**Solutions**:
1. **Check Required Fields**: Verify all required fields filled
2. **Check Validation**: Verify values are valid
3. **Check API**: Verify API is responding
4. **Check Storage**: Verify storage connection
5. **Check Permissions**: Verify user has permissions

---

## Import Issues

### CSV Import Fails

**Symptoms**:
- Import errors
- Validation errors
- Format errors

**Solutions**:
1. **Check Header Format**: Verify exact header format
2. **Check Required Fields**: Verify all required fields present
3. **Check Encoding**: Use UTF-8 encoding
4. **Check Format**: Use CSV format (commas, not semicolons)
5. **Check Data Types**: Verify data types are correct

**Common Errors**:
- **"Invalid header format"**: Header must match exactly
- **"Missing required field"**: Add missing required fields
- **"Invalid status value"**: Use valid status values
- **"Invalid data type"**: Verify numeric fields are numbers

---

## Performance Issues

### Slow Loading

**Symptoms**:
- Pages load slowly
- API calls slow
- Timeout errors

**Solutions**:
1. **Check Data Volume**: Reduce data volume if possible
2. **Check Filters**: Use filters to reduce data
3. **Check Network**: Verify network connection
4. **Check Server**: Check server performance
5. **Check Caching**: Enable caching if available

### Memory Issues

**Symptoms**:
- Browser crashes
- Out of memory errors
- Slow performance

**Solutions**:
1. **Reduce Data**: Reduce amount of data loaded
2. **Use Pagination**: Use pagination for large datasets
3. **Close Tabs**: Close unnecessary browser tabs
4. **Restart Browser**: Restart browser
5. **Check Resources**: Check system resources

---

## Browser Issues

### Browser Compatibility

**Supported Browsers**:
- Chrome (latest)
- Firefox (latest)
- Safari (latest)
- Edge (latest)

**Unsupported Browsers**:
- Internet Explorer
- Older browser versions

**Solutions**:
1. **Update Browser**: Update to latest version
2. **Use Modern Browser**: Use Chrome, Firefox, Safari, or Edge
3. **Check Features**: Verify browser supports required features

### Browser Console Errors

**Common Errors**:
- **CORS errors**: Check API CORS settings
- **Network errors**: Check network connectivity
- **JavaScript errors**: Check code for errors
- **API errors**: Check API responses

**Solutions**:
1. **Check Console**: Check browser console for errors
2. **Check Network Tab**: Check network requests
3. **Check API**: Verify API is responding
4. **Check Configuration**: Verify configuration

---

## Storage Issues

### Storage Connection Errors

**Symptoms**:
- Storage errors
- Connection failures
- Data not saving

**Solutions**:
1. **Check Connection String**: Verify connection string
2. **Check Permissions**: Verify storage permissions
3. **Check Storage Account**: Verify storage account exists
4. **Check Network**: Verify network connectivity
5. **Check Quotas**: Verify quotas not exceeded

### Data Not Persisting

**Symptoms**:
- Changes not saving
- Data lost
- Old data showing

**Solutions**:
1. **Check Storage**: Verify storage connection
2. **Check Permissions**: Verify write permissions
3. **Check API**: Verify API is saving data
4. **Check Transactions**: Verify transactions completing
5. **Check Logs**: Check storage logs

---

## Getting Help

### Before Asking for Help

1. **Check Documentation**: Review documentation
2. **Check FAQ**: Review FAQ for common questions
3. **Check Logs**: Check application logs
4. **Check Console**: Check browser console
5. **Reproduce**: Reproduce issue consistently

### When Asking for Help

Include:
- **Description**: Clear description of issue
- **Steps**: Steps to reproduce
- **Expected**: Expected behavior
- **Actual**: Actual behavior
- **Environment**: Browser, OS, version
- **Logs**: Relevant logs or errors
- **Screenshots**: Screenshots if applicable

### Where to Get Help

- **Documentation**: Check wiki documentation
- **FAQ**: Check FAQ page
- **GitHub Issues**: Open issue on GitHub
- **Community**: Engage with community

---

## Common Solutions

### Quick Fixes

1. **Refresh Page**: Often fixes UI issues
2. **Clear Cache**: Clears stale data
3. **Restart Browser**: Fixes browser issues
4. **Check Network**: Verifies connectivity
5. **Check Logs**: Provides error details

### System Checks

1. **Check Services**: Verify all services running
2. **Check Configuration**: Verify configuration correct
3. **Check Permissions**: Verify user has permissions
4. **Check Storage**: Verify storage accessible
5. **Check API**: Verify API responding

---

**Related**: [FAQ](/wiki/FAQ) | [Installation](/wiki/Installation) | [Configuration](/wiki/Configuration)

